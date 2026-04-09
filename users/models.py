from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now
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

GENDER_CHOICES = [
    ('Male', 'Male'),
    ('Female', 'Female'),
    ('Other', 'Other'),
]

class FamilyMember(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField(default=0)
    blood_group = models.CharField(max_length=10, choices=BLOOD_GROUP_CHOICES, default='A+')
    nationality = models.CharField(max_length=100, default='Indian')

    gender = models.CharField(max_length=10, choices=GENDER_CHOICES,default='Male')
    relation = models.CharField(max_length=50, default='Self')
    profile_photo = models.ImageField(upload_to='family_profiles/',null=True,blank=True)

    def __str__(self):
        return f"{self.name} ({self.relation}) - {self.blood_group}"



class FamilyMemberFile(models.Model):
    family_member = models.ForeignKey(FamilyMember, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='family_files/')
    description = models.TextField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"File for {self.family_member.name}: {self.description[:20]}..."
    

class Doctor(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    specialization = models.CharField(max_length=200)
    experience = models.IntegerField()
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2)

    phone = models.CharField(max_length=15)
    image = models.ImageField(upload_to="doctors/")

    about = models.TextField()

    qualification = models.CharField(max_length=200, blank=True, null=True)
    location = models.CharField(max_length=200, blank=True, null=True)
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.user.get_full_name()


from datetime import date

class Appointment(models.Model):

    doctor = models.ForeignKey("Doctor", on_delete=models.CASCADE)
    patient = models.ForeignKey(User, on_delete=models.CASCADE)

    full_name = models.CharField(max_length=100)
    age = models.IntegerField()
    phone = models.CharField(max_length=15)
    gender = models.CharField(max_length=10)
    email = models.EmailField(blank=True, null=True)

    date = models.DateField()
    time = models.TimeField()

    payment_method = models.CharField(max_length=10, choices=[
        ("cash", "Cash"),
        ("online", "Online")
    ])

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.doctor}"
    
    