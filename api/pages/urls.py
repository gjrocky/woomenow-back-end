from django.urls import path

from api.pages.views import FAQsPageAPIViews, BusinessPageAPIView, AboutPageAPIView

app_name = "pages"

urlpatterns = [
    path("faqs/", FAQsPageAPIViews.as_view(), name="faqs"),
    path("business/", BusinessPageAPIView.as_view(), name="business"),
    path("about/", AboutPageAPIView.as_view(), name="about"),
]
