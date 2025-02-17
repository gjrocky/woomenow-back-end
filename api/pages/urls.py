from django.urls import path

from api.pages.views import FAQsPageAPIViews, BusinessPageAPIView, AboutPageAPIView, PricingPageAPIView, \
    JoinTheWooPageAPIView, InfluencerPageAPIView

app_name = "pages"

urlpatterns = [
    path("faqs/", FAQsPageAPIViews.as_view(), name="faqs"),
    path("business/", BusinessPageAPIView.as_view(), name="business"),
    path("about/", AboutPageAPIView.as_view(), name="about"),
    path("pricing/", PricingPageAPIView.as_view(), name="about"),
    path("join-the-woo/", JoinTheWooPageAPIView.as_view(), name="join-the-woo"),
    path("influencer/<pk>/", InfluencerPageAPIView.as_view(), name="influencer-detail"),
]
