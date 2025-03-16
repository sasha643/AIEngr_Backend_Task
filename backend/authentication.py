from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

import jwt
import os
from authentication.models import User 

SECRET_KEY = os.getenv("SECRET_KEY")

class CookieJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_token = request.COOKIES.get("auth_token")
        if not auth_token:
            return None 
        
        try:
            payload = jwt.decode(auth_token, SECRET_KEY, algorithms=["HS256"])
            user = User.objects.get(id=payload["user_id"])
        except (jwt.ExpiredSignatureError, jwt.DecodeError, User.DoesNotExist):
            raise AuthenticationFailed("Invalid token or user not found")

        return (user, None) 
