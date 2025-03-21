from django.urls import path

from api.forms.views import IPLocationAPIView, ContactAPIView, InvitationAPIView, ReviewAPIView, JoinTheWooAPIView, \
    BookmarkAPIView, ReviewPostAPIView, PendingReviewAPIView, BecomeAnInfluencerAPIView, RestaurantInvitationAPIView, \
    CampaignAPIView

app_name = "forms"

urlpatterns = [
    path("location/", IPLocationAPIView.as_view(), name="location"),
    path("contact/", ContactAPIView.as_view(), name="contact"),
    path("join-the-woo/", JoinTheWooAPIView.as_view(), name="join-the-woo"),
    path("invitation/", InvitationAPIView.as_view(), name="invitation"),
    path("reviews/", ReviewAPIView.as_view(), name="reviews"),
    path("review/", ReviewPostAPIView.as_view(), name="review"),
    path("pending-reviews/", PendingReviewAPIView.as_view(), name="pending-reviews"),
    path("become-an-influencer/", BecomeAnInfluencerAPIView.as_view(), name="become-an-influencer"),
    path("restaurant-invitation/", RestaurantInvitationAPIView.as_view(), name="restaurant-invitation"),
    path("bookmark/", BookmarkAPIView.as_view(), name="bookmark"),
    path("campaign/<slug>/", CampaignAPIView.as_view(), name="campaign"),

]
