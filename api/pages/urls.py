from django.urls import path

from api.pages.views import FAQsPageAPIViews

app_name = "pages"

urlpatterns = [
    path("faqs/", FAQsPageAPIViews.as_view(), name="faqs"),
]
