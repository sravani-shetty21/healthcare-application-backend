from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import LoginSerializer,RegisterSerializer, FamilyMemberSerializer, FamilyMemberFileSerializer
from rest_framework import viewsets, permissions,filters
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import FamilyMember, FamilyMemberFile

class LoginView(APIView):

    def post(self, request):

        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():

            user = serializer.validated_data

            refresh = RefreshToken.for_user(user)

            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "username": user.username
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class RegisterView(APIView):

    def post(self, request):

        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            refresh = RefreshToken.for_user(user)

            return Response({
                "message": "User registered successfully",
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh)
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FamilyMemberViewSet(viewsets.ModelViewSet):
    serializer_class = FamilyMemberSerializer
    permission_classes = [permissions.IsAuthenticated]

    # SEARCH FUNCTION
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def get_queryset(self):

        queryset = FamilyMember.objects.filter(user=self.request.user)

        # SORT BY AGE ASCENDING
        return queryset.order_by('age')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def add_file(self, request, pk=None):

        member = self.get_object()

        files = request.FILES.getlist('file')
        descriptions = request.data.getlist('description')

        created_files = []

        for i, file in enumerate(files):

            desc = descriptions[i] if i < len(descriptions) else ""

            file_obj = FamilyMemberFile.objects.create(
                family_member=member,
                file=file,
                description=desc
            )

            created_files.append(file_obj)

        serializer = FamilyMemberFileSerializer(created_files, many=True)

        return Response(serializer.data, status=201)