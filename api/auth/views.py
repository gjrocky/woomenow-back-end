import random

from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from django.core.mail import send_mail
from django.utils.timezone import now, timedelta
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from api.auth.serializers import UserSerializer
from apps.main.models import OTPVerification
from apps.users.models import User


class GoogleLoginView(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client
    authentication_classes = []
    callback_url = 'http://localhost:3000'

    def get_response(self):
        response = super().get_response()
        if response.status_code == 200:
            user = self.user

            access_token = AccessToken.for_user(user)
            refresh_token = RefreshToken.for_user(user)
            return Response({
                'status': 'success',
                'access_token': str(access_token),
                'refresh_token': str(refresh_token),
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                }
            })
        return response

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)


class UserView(APIView):
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser,)

    def get(self, request, *args, **kwargs):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            print('saving')
            serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


def send_otp_email(email, otp_code):
    """Helper function to send OTP via email"""
    send_mail(
        "Your OTP Code",
        f"Your OTP code is {otp_code}. It expires in 10 minutes.",
        "your_email@gmail.com",
        [email],
        fail_silently=False,
    )


class SignupAPIView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")
        password = request.data.get("password")
        confirm_password = request.data.get("confirm_password")

        if password != confirm_password:
            return Response({"error": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({"error": "User already exists"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create(first_name=first_name, last_name=last_name, email=email)
        user.set_password(password)
        user.is_active = False
        user.save()

        # Generate OTP
        otp_code = str(random.randint(100000, 999999))
        OTPVerification.objects.create(user=user, otp=otp_code, expires_at=now() + timedelta(minutes=10))

        # Send OTP via Email
        send_otp_email(email, otp_code)

        return Response({"message": "OTP sent to email"}, status=status.HTTP_201_CREATED)


class VerifyOTPAPIView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        otp_code = request.data.get("otp")

        try:
            user = User.objects.get(email=email)
            otp_entry = OTPVerification.objects.get(user=user)
            user.is_active = True
            user.save()

            if otp_entry.otp == otp_code and otp_entry.is_valid():
                otp_entry.delete()  # OTP used, remove entry
                return Response({"message": "Email verified"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)

        except (User.DoesNotExist, OTPVerification.DoesNotExist):
            return Response({"error": "User or OTP not found"}, status=status.HTTP_400_BAD_REQUEST)


class ResendOTPAPIView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")

        try:
            user = User.objects.get(email=email)
            otp_entry, created = OTPVerification.objects.get_or_create(user=user)

            otp_entry.otp = str(random.randint(100000, 999999))
            otp_entry.expires_at = now() + timedelta(minutes=10)
            otp_entry.save()

            send_otp_email(email, otp_entry.otp)

            return Response({"message": "OTP resent"}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordAPIView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        try:
            user = User.objects.get(email=email)
            otp_entry, created = OTPVerification.objects.get_or_create(user=user)

            otp_entry.otp = str(random.randint(100000, 999999))
            otp_entry.expires_at = now() + timedelta(minutes=10)
            otp_entry.save()

            send_otp_email(email, otp_entry.otp)

            return Response({"message": "OTP resent"}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordAPIView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        password = request.data.get("password")
        confirm_password = request.data.get("confirm_password")

        if password != confirm_password:
            return Response({"error": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            user.set_password(password)
            user.save()
            return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_400_BAD_REQUEST)
