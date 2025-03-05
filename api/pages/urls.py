from django.urls import path

from api.pages.views import FAQsPageAPIViews, BusinessPageAPIView, AboutPageAPIView, PricingPageAPIView, \
    JoinTheWooPageAPIView, InfluencerPageAPIView, InfluencerListingPageAPIView, RestaurantListingPageAPIView, \
    RestaurantPageAPIView, UpdateInfluencerPageAPIView, RestaurantReviewsAPIView, RestaurantRecommendationAPIView, \
    RestaurantDetailsAPIView

from rest_framework.authtoken.views import obtain_auth_token


app_name = "pages"

urlpatterns = [
    path("auth/", obtain_auth_token),
    path("faqs/", FAQsPageAPIViews.as_view(), name="faqs"),
    path("business/", BusinessPageAPIView.as_view(), name="business"),
    path("about/", AboutPageAPIView.as_view(), name="about"),
    path("pricing/", PricingPageAPIView.as_view(), name="about"),
    path("join-the-woo/", JoinTheWooPageAPIView.as_view(), name="join-the-woo"),
    path("influencer/<pk>/", InfluencerPageAPIView.as_view(), name="influencer-detail"),
    path("influencers/", InfluencerListingPageAPIView.as_view(), name="influencers"),
    path("influencer-profile/", UpdateInfluencerPageAPIView.as_view(), name="influencer-profile"),
    path("restaurants/", RestaurantListingPageAPIView.as_view(), name="restaurants"),
    path("restaurant/<pk>/", RestaurantPageAPIView.as_view(), name="restaurant-detail"),
    path("restaurant-reviews/", RestaurantReviewsAPIView.as_view(), name="restaurant-reviews"),
    path("restaurant-recommendation/", RestaurantRecommendationAPIView.as_view(), name="restaurant-recommendation"),
    path("restaurant-detail/", RestaurantDetailsAPIView.as_view(), name="restaurant-recommendation"),
    path("restaurant-menus/", RestaurantDetailsAPIView.as_view(), name="restaurant-menus"),
    path("restaurant-images/", RestaurantDetailsAPIView.as_view(), name="restaurant-images"),
]
