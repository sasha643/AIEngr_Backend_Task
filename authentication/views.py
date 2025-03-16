from django.core.mail import send_mail
from django.contrib.auth import authenticate, login, logout
import random
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .serializers import *
from .models import User
from backend import settings



class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.is_verified = False
            otp = str(random.randint(100000, 999999))
            user.otp = otp
            user.save()

            send_mail(
                subject="Email Verification",
                message=f"Your OTP for verification is: {otp}",
                from_email=settings.EMAIL_HOST_USER, 
                recipient_list=[user.email],
                fail_silently=True,
            )

            return Response({'message': 'OTP sent to your email for verification'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class VerifyOTPView(APIView):
    def post(self, request):
        serializer = OTPVerificationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = User.objects.get(email=serializer.validated_data['email'])
                if user.otp == serializer.validated_data['otp']:
                    user.is_verified = True
                    user.otp = None
                    user.save()
                    return Response({'message': 'User verified'}, status=status.HTTP_200_OK)
                return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(email=email, password=password)
            if user and user.is_verified:
                login(request, user)
                response = Response({'message': 'Login successful'}, status=status.HTTP_200_OK)
                response.set_cookie('auth_token', 'sessionid', httponly=True, secure=True)
                return response
            return Response({'error': 'Invalid credentials or user not verified'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)