from django.core.mail import send_mail
from django.contrib.auth import authenticate
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication

from drf_spectacular.utils import extend_schema
from .models import User
from .serializers import RegisterUserSerializer, VerifyOTPSerializer, LoginUserSerializer
from backend import settings

from dotenv import load_dotenv
import jwt
import os
import random

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")


@method_decorator(ensure_csrf_cookie, name="dispatch")
class GetCSRFToken(APIView):
    @extend_schema(responses={200: {"csrfToken": "string"}})
    def get(self, request):
        return Response({"csrfToken": get_token(request)})


class RegisterView(APIView):
    @extend_schema(
        request=RegisterUserSerializer,
        responses={200: {"message": "OTP sent to your email."}}
    )
    def post(self, request):
        serializer = RegisterUserSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            password = serializer.validated_data["password"]

            if User.objects.filter(email=email).exists():
                return Response({"error": "Email already registered"}, status=400)

            otp = random.randint(100000, 999999)

            user = User.objects.create(
                email=email,
                password=password, 
                otp=otp,
                is_verified=False
            )

            send_mail(
                subject="Email Verification",
                message=f"Your OTP for verification is: {otp}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=True,
            )

            return Response({"message": "OTP sent to your email."}, status=200)

        return Response(serializer.errors, status=400)
    

class VerifyOTPView(APIView):
    @extend_schema(
        request=VerifyOTPSerializer,
        responses={200: {"message": "User verified successfully."}, 400: {"error": "Invalid OTP"}}
    )
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            otp_entered = serializer.validated_data["otp"]

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=404)

            if user.is_verified:
                return Response({"message": "User already verified. Please log in."}, status=200)

            if str(user.otp) == str(otp_entered):
                user.is_verified = True
                user.otp = None
                user.save()

                return Response({"message": "User verified successfully."}, status=200)

            return Response({"error": "Invalid OTP"}, status=400)

        return Response(serializer.errors, status=400)
    

class LoginView(APIView):
    @extend_schema(
        request=LoginUserSerializer,
        responses={200: {"message": "Login successful."}}
    )
    def post(self, request):
        serializer = LoginUserSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            password = serializer.validated_data["password"]

            user = authenticate(request, username=email, password=password)
            if user:
                auth_token = jwt.encode({"user_id": user.id}, SECRET_KEY, algorithm="HS256")

                response = Response({"message": "Login successful."}, status=200)
                response.set_cookie(
                    "auth_token", auth_token, httponly=True, secure=True, samesite="Lax"
                )
                return response

            return Response({"error": "Invalid credentials"}, status=401)

        return Response(serializer.errors, status=400)


class LogoutView(APIView):
    @extend_schema(responses={200: {"message": "Logout successful."}})
    def post(self, request):
        response = Response({"message": "Logout successful."})
        response.delete_cookie("auth_token")
        return response


class UserDetailsView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: {"email": "string"}})
    def get(self, request):
        auth_token = request.COOKIES.get("auth_token")
        if not auth_token:
            return Response({"error": "Not authenticated"}, status=401)

        payload = jwt.decode(auth_token, SECRET_KEY, algorithms=["HS256"])
        user = User.objects.get(id=payload["user_id"])

        return Response({"email": user.email, "is_verified":user.is_verified})
