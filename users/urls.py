from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LoginView, RegisterView, FamilyMemberViewSet, DoctorList, DoctorDetail,BookAppointmentView,AvailableSlots, SummarizeFile
 

router = DefaultRouter()
router.register(r'users', FamilyMemberViewSet, basename='family-member')

urlpatterns = [
    # Auth
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path("doctors/", DoctorList.as_view(), name="doctors"),
    path("doctors/<int:pk>/", DoctorDetail.as_view(), name="doctor-detail"), 
    path("appointments/", BookAppointmentView.as_view(), name="book-appointment"),  
    path("doctors/<int:doctor_id>/slots/", AvailableSlots.as_view()),
    path('', include(router.urls)),

    path("summarize-report/", SummarizeFile.as_view(), name='summarize-report'),
]


