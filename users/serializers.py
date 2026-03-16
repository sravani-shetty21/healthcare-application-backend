from django.contrib.auth.models import User
from .models import UserProfile
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import FamilyMember, FamilyMemberFile

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):

        user = authenticate(
            username=data["username"],
            password=data["password"]
        )

        if not user:
            raise serializers.ValidationError("Invalid credentials")

        return user
    

class RegisterSerializer(serializers.Serializer):

    first_name = serializers.CharField()
    last_name = serializers.CharField()
    phone_number = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):

        email = validated_data["email"]

        if User.objects.filter(username=email).exists():
            raise serializers.ValidationError("Email already exists")

        user = User.objects.create_user(
            username=email,
            email=email,
            password=validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"]
        )

        UserProfile.objects.create(
            user=user,
            phone_number=validated_data["phone_number"]
        )

        return user
    

class FamilyMemberFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = FamilyMemberFile
        fields = ['id', 'file', 'description']

class FamilyMemberSerializer(serializers.ModelSerializer):
    files = FamilyMemberFileSerializer(many=True, read_only=True)  

    class Meta:
        model = FamilyMember
        fields = ['id', 'user', 'name', 'age', 'blood_group', 'nationality','files']
        read_only_fields = ['user']  