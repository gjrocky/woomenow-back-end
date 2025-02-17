from django.urls import path

from api.auth.views import GoogleLoginView, UserView

app_name = "auth"

urlpatterns = [
    path('google/login', GoogleLoginView.as_view(), name='social-google-login'),
    path('', UserView.as_view(), name='user'),
]
