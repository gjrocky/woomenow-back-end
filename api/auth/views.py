import random
from datetime import datetime

from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from django.conf import settings
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
from api.helper import password_checker
from apps.main.helper import email_dict
from apps.main.models import OTPVerification
from apps.users.models import User
from send_email import send_email


class GoogleLoginView(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client
    authentication_classes = []
    callback_url = settings.CALLBACK_URL

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
        data = request.data.copy()
        date_str = request.data.get('date_of_birth')

        try:
            # Try parsing full ISO format first
            dt_object = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError:
            try:
                # If that fails, try parsing only YYYY-MM-DD
                dt_object = datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                raise ValueError(f"Invalid date format: {date_str}")
        formatted_date = dt_object.date()
        data['date_of_birth'] = formatted_date
        serializer = UserSerializer(request.user, data=data, partial=True)
        if serializer.is_valid(raise_exception=True):
            print('saving')
            serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class SignupAPIView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")
        password = request.data.get("password")
        confirm_password = request.data.get("confirm_password")

        if password != confirm_password:
            return Response({"error": "Passwords are not matched"}, status=status.HTTP_400_BAD_REQUEST)

        password, is_not_valid_pass = password_checker(password)

        if is_not_valid_pass:
            return Response({"error": password}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({"error": "User already exists"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create(first_name=first_name, last_name=last_name, email=email)
        user.set_password(password)
        user.is_active = False
        user.save()

        # Generate OTP
        otp_code = str(random.randint(100000, 999999))
        OTPVerification.objects.create(user=user, otp=otp_code, expires_at=now() + timedelta(minutes=10))

        e = [email]
        body = 'emails/confirmation.html'
        context = dict(username=user.first_name, otp=otp_code, **email_dict)
        subject_context = dict(subject='Confirm your email address.')
        send_email(e, body, context, subject_context)

        return Response({"message": "OTP sent to email"}, status=status.HTTP_201_CREATED)


class VerifyOTPAPIView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        otp_code = request.data.get("otp")

        try:
            user = User.objects.get(email=email)
            otp_entry = OTPVerification.objects.get(user=user)
            if not user.is_active:
                e = [email]
                body = 'emails/welcome-for-users.html'
                context = dict(username=user.first_name, **email_dict)
                subject_context = dict(subject='Welcome to WooMeNow!')
                send_email(e, body, context, subject_context)
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
            otp = str(random.randint(100000, 999999))

            otp_entry.otp = otp
            otp_entry.expires_at = now() + timedelta(minutes=10)
            otp_entry.save()

            e = [email]
            body = 'emails/resend.html'
            context = dict(username=user.first_name, otp=otp, **email_dict)
            subject_context = dict(subject='Your New Verification Code.')
            send_email(e, body, context, subject_context)

            return Response({"message": "OTP resent"}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordAPIView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        try:
            user = User.objects.get(email=email)
            otp_entry, created = OTPVerification.objects.get_or_create(user=user)
            otp = str(random.randint(100000, 999999))
            otp_entry.otp = otp
            otp_entry.expires_at = now() + timedelta(minutes=10)
            otp_entry.save()

            e = [email]
            body = 'emails/reset.html'
            context = dict(username=user.first_name, otp=otp, **email_dict)
            subject_context = dict(subject='Reset your password.')
            send_email(e, body, context, subject_context)

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

        password, is_not_valid_pass = password_checker(password)

        if is_not_valid_pass:
            return Response({"error": password}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            user.set_password(password)
            user.save()
            return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_400_BAD_REQUEST)
