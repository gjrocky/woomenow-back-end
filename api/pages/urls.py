from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from api.pages.views import FAQsPageAPIViews, BusinessPageAPIView, AboutPageAPIView, PricingPageAPIView, \
    JoinTheWooPageAPIView, InfluencerPageAPIView, InfluencerListingPageAPIView, RestaurantListingPageAPIView, \
    RestaurantPageAPIView, UpdateInfluencerPageAPIView, RestaurantReviewsAPIView, RestaurantRecommendationAPIView, \
    RestaurantDetailsAPIView, RestaurantDetailAPIView, RestaurantCreateAPIView, RestaurantInviteAPIView, HomePageAPIView

app_name = "pages"

urlpatterns = [
    path("auth/", obtain_auth_token),
    path("home/", HomePageAPIView.as_view(), name="home"),
    path("faqs/", FAQsPageAPIViews.as_view(), name="faqs"),
    path("business/", BusinessPageAPIView.as_view(), name="business"),
    path("about/", AboutPageAPIView.as_view(), name="about"),
    path("pricing/", PricingPageAPIView.as_view(), name="about"),
    path("join-the-woo/", JoinTheWooPageAPIView.as_view(), name="join-the-woo"),
    path("influencer/<slug>/", InfluencerPageAPIView.as_view(), name="influencer-detail"),
    path("influencers/", InfluencerListingPageAPIView.as_view(), name="influencers"),
    path("influencer-profile/", UpdateInfluencerPageAPIView.as_view(), name="influencer-profile"),
    path("restaurants/", RestaurantListingPageAPIView.as_view(), name="restaurants"),
    path("restaurant/<slug>/", RestaurantPageAPIView.as_view(), name="restaurant-detail"),
    path("restaurant-reviews/", RestaurantReviewsAPIView.as_view(), name="restaurant-reviews"),
    path("restaurant-recommendation/", RestaurantRecommendationAPIView.as_view(), name="restaurant-recommendation"),
    path("restaurant-detail/", RestaurantDetailsAPIView.as_view(), name="restaurant-detail"),
    path("restaurant-info/<pk>/", RestaurantDetailAPIView.as_view(), name="restaurant-info"),
    path("restaurant-menus/", RestaurantDetailsAPIView.as_view(), name="restaurant-menus"),
    path("restaurant-images/", RestaurantDetailsAPIView.as_view(), name="restaurant-images"),
    path("restaurant-create/", RestaurantCreateAPIView.as_view(), name="restaurant-create"),
    path("restaurant-invite/", RestaurantInviteAPIView.as_view(), name="restaurant-invite"),
]
