from django.urls import path

from api.forms.views import IPLocationAPIView, ContactAPIView, InvitationAPIView, ReviewAPIView, JoinTheWooAPIView

app_name = "forms"

urlpatterns = [
    path("location/", IPLocationAPIView.as_view(), name="location"),
    path("contact/", ContactAPIView.as_view(), name="contact"),
    path("join-the-woo/", JoinTheWooAPIView.as_view(), name="join-the-woo"),
    path("invitation/", InvitationAPIView.as_view(), name="invitation"),
    path("reviews/", ReviewAPIView.as_view(), name="review"),

]
