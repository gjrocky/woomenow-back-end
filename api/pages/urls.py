from django.urls import path

from api.pages.views import FAQsPageAPIViews, BusinessAPIView

app_name = "pages"

urlpatterns = [
    path("faqs/", FAQsPageAPIViews.as_view(), name="faqs"),
    path("business/", BusinessAPIView.as_view(), name="business"),
]
