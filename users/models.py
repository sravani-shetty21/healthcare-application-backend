from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)

    def __str__(self):
        return self.user.email
    


BLOOD_GROUP_CHOICES = [
    ('A+', 'A+'),
    ('A-', 'A-'),
    ('B+', 'B+'),
    ('B-', 'B-'),
    ('AB+', 'AB+'),
    ('AB-', 'AB-'),
    ('O+', 'O+'),
    ('O-', 'O-'),
]

class FamilyMember(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField(default=0)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, default='O+')
    nationality = models.CharField(max_length=100, default='Indian')
    def _str_(self):
        return f"{self.name} ({self.blood_group})"



class FamilyMemberFile(models.Model):
    family_member = models.ForeignKey(FamilyMember, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='family_files/')
    description = models.TextField()

    def _str_(self):
        return f"File for {self.family_member.name}: {self.description[:20]}..."