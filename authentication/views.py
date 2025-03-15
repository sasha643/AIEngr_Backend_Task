from django.core.mail import send_mail
import random
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .serializers import RegisterSerializer
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