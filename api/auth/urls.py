from django.urls import path

from api.auth.views import GoogleLoginView, UserView, SignupAPIView, VerifyOTPAPIView, ResendOTPAPIView, \
    ResetPasswordAPIView, ChangePasswordAPIView

app_name = "auth"

urlpatterns = [
    path('google/login', GoogleLoginView.as_view(), name='social-google-login'),

    path("signup/", SignupAPIView.as_view(), name="signup"),
    path("verify-otp/", VerifyOTPAPIView.as_view(), name="verify_otp"),
    path("resend-otp/", ResendOTPAPIView.as_view(), name="resend_otp"),
    path("forgot-password/", ResetPasswordAPIView.as_view(), name="forgot-password"),
    path("change-password/", ChangePasswordAPIView.as_view(), name="change-password"),
    path('', UserView.as_view(), name='user'),
]
