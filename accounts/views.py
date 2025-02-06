# accounts/views.py
from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny
from rest_framework.serializers import ModelSerializer
from records.models import Patient
from appointments.models import Doctor
from rest_framework_simplejwt.views import TokenObtainPairView

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password', 'email')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Create Patient or Doctor profile based on role
        role = request.data.get('role')
        if role == 'patient':
            Patient.objects.create(user=user, name=user.username)
        elif role == 'doctor':
            Doctor.objects.create(user=user, specialization='General')

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            user = User.objects.get(username=request.data['username'])
            if hasattr(user, 'patient'):
                response.data['redirect'] = '/patient/patient-portal/'  # Correct URL
            elif hasattr(user, 'doctor'):
                response.data['redirect'] = '/doctor/doctor-portal/'  # Correct URL
        return response
    

def login_view(request):
    return render(request, 'accounts/login.html')

def register_view(request):
    return render(request, 'accounts/register.html')
