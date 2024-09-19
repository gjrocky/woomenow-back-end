from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token

from api.views import StateAPIView, CategoryAPIView, FranchiseAPIView

app_name = "api"

urlpatterns = [
    path("categories/", CategoryAPIView.as_view(), name="categories"),
    path("states/", StateAPIView.as_view(), name="states"),
    path("franchise/", FranchiseAPIView.as_view(), name="franchise"),
    path("auth/", obtain_auth_token),
    path("pages/", include("api.pages.urls")),

    path("forms/", include("api.forms.urls")),
]
