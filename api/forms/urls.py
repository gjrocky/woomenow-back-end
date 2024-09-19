from django.urls import path

from api.forms.views import IPLocationAPIView, ContactAPIView, InvitationAPIView, ReviewAPIView

app_name = "forms"

urlpatterns = [
    path("location/", IPLocationAPIView.as_view(), name="location"),
    path("contact/", ContactAPIView.as_view(), name="contact"),
    path("invitation/", InvitationAPIView.as_view(), name="invitation"),
    path("reviews/", ReviewAPIView.as_view(), name="review"),

]
