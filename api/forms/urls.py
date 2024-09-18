from django.urls import path

from api.forms.views import IPLocationAPIView, ContactAPIView

app_name = "forms"

urlpatterns = [
    path("location/", IPLocationAPIView.as_view(), name="location"),
    path("contact/", ContactAPIView.as_view(), name="contact"),
]
