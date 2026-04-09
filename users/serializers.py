from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from rest_framework import serializers

from .models import UserProfile,FamilyMember,FamilyMemberFile,Doctor,Appointment

# LOGIN SERIALIZER

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(
            username=data.get("username"),
            password=data.get("password")
        )

        if not user:
            raise serializers.ValidationError("Invalid credentials")

        return user

# REGISTER SERIALIZER

class RegisterSerializer(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    phone_number = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        email = validated_data.get("email")

        # Check if user already exists
        if User.objects.filter(username=email).exists():
            raise serializers.ValidationError("Email already exists")

        # Create user
        user = User.objects.create_user(
            username=email,
            email=email,
            password=validated_data.get("password"),
            first_name=validated_data.get("first_name"),
            last_name=validated_data.get("last_name")
        )

        # Create user profile
        UserProfile.objects.create(
            user=user,
            phone_number=validated_data.get("phone_number")
        )

        return user

# FAMILY MEMBER FILE SERIALIZER

class FamilyMemberFileSerializer(serializers.ModelSerializer):

    class Meta:
        model = FamilyMemberFile
        fields = [
            "id",
            "file",
            "description",
            "uploaded_at"
        ]

# FAMILY MEMBER SERIALIZER

class FamilyMemberSerializer(serializers.ModelSerializer):
    files = FamilyMemberFileSerializer(many=True, read_only=True)

    class Meta:
        model = FamilyMember
        fields = ["id","user","name","age","gender","relation","blood_group","nationality","profile_photo","files"]
        read_only_fields = ["user"]

    # Handle update (including image update)
    def update(self, instance, validated_data):

        instance.name = validated_data.get("name", instance.name)
        instance.age = validated_data.get("age", instance.age)
        instance.gender = validated_data.get("gender", instance.gender)
        instance.relation = validated_data.get("relation", instance.relation)
        instance.blood_group = validated_data.get("blood_group", instance.blood_group)
        instance.nationality = validated_data.get("nationality", instance.nationality)

        # Update profile photo only if provided
        if "profile_photo" in validated_data:
            instance.profile_photo = validated_data.get("profile_photo")

        instance.save()
        return instance

# DOCTOR SERIALIZER

class DoctorSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    available_dates = serializers.SerializerMethodField()
    available_times = serializers.SerializerMethodField()

    class Meta:
        model = Doctor
        fields = "__all__"

    def get_image(self, obj):
        request = self.context.get("request")

        if obj.image:
            return request.build_absolute_uri(obj.image.url)

        return None

    def get_name(self, obj):
        return obj.user.get_full_name()

    def get_available_dates(self, obj):
        from datetime import date, timedelta

        today = date.today()

        return [
            (today + timedelta(days=i)).isoformat()
            for i in range(5)
        ]

    def get_available_times(self, obj):
        return [
            "11:00 AM",
            "03:00 PM",
            "05:00 PM"
        ]

# APPOINTMENT SERIALIZER

class AppointmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Appointment
        fields = "__all__"
        