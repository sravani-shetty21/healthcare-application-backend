import os
from io import BytesIO
from datetime import datetime

import numpy as np
import PyPDF2
import easyocr

from PIL import Image
from dotenv import load_dotenv
from pdf2image import convert_from_bytes
from transformers import pipeline
from openai import OpenAI

from django.contrib.auth.models import User

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser

from rest_framework_simplejwt.tokens import RefreshToken

from .models import FamilyMember,FamilyMemberFile,Doctor,Appointment

from .serializers import LoginSerializer,RegisterSerializer,FamilyMemberSerializer,FamilyMemberFileSerializer,DoctorSerializer


# AUTHENTICATION (LOGIN / REGISTER)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.validated_data
        refresh = RefreshToken.for_user(user)

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "username": user.username
        })


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()
        refresh = RefreshToken.for_user(user)

        return Response({
            "message": "User registered successfully",
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        }, status=status.HTTP_201_CREATED)

# FAMILY MEMBER MANAGEMENT

class FamilyMemberViewSet(viewsets.ModelViewSet):
    serializer_class = FamilyMemberSerializer
    permission_classes = [permissions.IsAuthenticated]

    parser_classes = [MultiPartParser, FormParser]

    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]

    def get_queryset(self):
        return FamilyMember.objects.filter(
            user=self.request.user
        ).order_by("age")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def partial_update(self, request, *args, **kwargs):
        print("FILES:", request.FILES)
        return super().partial_update(request, *args, **kwargs)

    # ADD FILE (SINGLE FILE UPLOAD)
  
    @action(detail=True, methods=["post"])
    def add_file(self, request, pk=None):
        member = self.get_object()

        file = request.FILES.get("file")
        description = request.data.get("description", "")

        if not file:
            return Response(
                {"error": "No file provided"},
                status=status.HTTP_400_BAD_REQUEST
            )

        file_obj = FamilyMemberFile.objects.create(
            family_member=member,
            file=file,
            description=description
        )

        serializer = FamilyMemberFileSerializer(file_obj)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # DELETE FILE

    @action(
        detail=True,
        methods=["delete"],
        url_path="delete-file/(?P<file_id>[^/.]+)"
    )
    def delete_file(self, request, pk=None, file_id=None):
        try:
            file = FamilyMemberFile.objects.get(
                id=file_id,
                family_member_id=pk
            )
            file.delete()

            return Response(
                {"message": "Deleted successfully"},
                status=status.HTTP_200_OK
            )

        except FamilyMemberFile.DoesNotExist:
            return Response(
                {"error": "File not found"},
                status=status.HTTP_404_NOT_FOUND
            )

# DOCTOR APIs

class DoctorList(APIView):
    def get(self, request):
        doctors = Doctor.objects.filter(available=True)

        serializer = DoctorSerializer(
            doctors,
            many=True,
            context={"request": request}
        )

        return Response(serializer.data)


class DoctorDetail(APIView):
    def get(self, request, pk):
        try:
            doctor = Doctor.objects.get(pk=pk)
        except Doctor.DoesNotExist:
            return Response(
                {"error": "Doctor not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = DoctorSerializer(
            doctor,
            context={"request": request}
        )

        return Response(serializer.data)

# APPOINTMENT BOOKING

class BookAppointmentView(APIView):
    def post(self, request):
        doctor_id = request.data.get("doctor")
        date = request.data.get("date")
        time = request.data.get("time")

        # Check if slot already booked
        if Appointment.objects.filter(
            doctor_id=doctor_id,
            date=date,
            time=time
        ).exists():
            return Response(
                {"error": "Slot already booked"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create appointment
        Appointment.objects.create(
            doctor_id=doctor_id,
            date=date,
            time=time,
            full_name=request.data.get("full_name"),
            age=request.data.get("age"),
            phone=request.data.get("phone"),
            gender=request.data.get("gender"),
            email=request.data.get("email"),
            payment=request.data.get("payment"),
        )

        return Response(
            {"success": "Appointment booked successfully"},
            status=status.HTTP_201_CREATED
        )

# AVAILABLE SLOTS

class AvailableSlots(APIView):
    def get(self, request, doctor_id):
        date = request.GET.get("date")

        all_slots = [
            "10:00:00",
            "11:00:00",
            "12:00:00",
            "15:00:00",
            "16:00:00"
        ]

        booked_slots = Appointment.objects.filter(
            doctor_id=doctor_id,
            date=date
        ).values_list("time", flat=True)

        available_slots = [
            slot for slot in all_slots
            if slot not in booked_slots
        ]

        return Response(available_slots)

# FILE SUMMARIZATION (OCR + AI)

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

summarizer = None
ocr_reader = None


def get_ocr():
    global ocr_reader

    if ocr_reader is None:
        ocr_reader = easyocr.Reader(["en"], gpu=False)

    return ocr_reader


def extract_text(file):
    filename = file.name.lower()
    file_bytes = file.read()

    reader = get_ocr()

    # -------- PDF --------
    if filename.endswith(".pdf"):
        text = ""
        pdf_stream = BytesIO(file_bytes)
        pdf_reader = PyPDF2.PdfReader(pdf_stream)

        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + " "

        # fallback OCR for scanned PDFs
        if not text.strip():
            images = convert_from_bytes(file_bytes)

            for img in images:
                result = reader.readtext(np.array(img), detail=0)
                text += " ".join(result) + " "

        return text.strip()

    # -------- IMAGE --------
    elif filename.endswith((".png", ".jpg", ".jpeg")):
        image = Image.open(BytesIO(file_bytes)).convert("RGB")
        result = reader.readtext(np.array(image), detail=0)
        return " ".join(result).strip()

    return ""


def summarize_text(text):
    global summarizer

    if summarizer is None:
        summarizer = pipeline(
            "summarization",
            model="sshleifer/distilbart-cnn-12-6"
        )

    if not text:
        return "No readable content found."

    max_chunk = 1000

    chunks = [
        text[i:i + max_chunk]
        for i in range(0, len(text), max_chunk)
    ]

    summaries = []

    for chunk in chunks:
        result = summarizer(
            chunk,
            max_length=120,
            min_length=40,
            do_sample=False
        )
        summaries.append(result[0]["summary_text"])

    return " ".join(summaries)


class SummarizeFile(APIView):
    def post(self, request):
        try:
            file = request.FILES.get("file")

            if not file:
                return Response(
                    {"error": "No file uploaded"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            text = extract_text(file)

            if not text:
                return Response(
                    {"error": "No readable text found"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            summary = summarize_text(text)

            return Response({"summary": summary})

        except Exception as error:
            return Response(
                {"error": str(error)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
