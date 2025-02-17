from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

from api.views import StateAPIView, CategoryAPIView, FranchiseAPIView

app_name = "api"

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path("categories/", CategoryAPIView.as_view(), name="categories"),
    path("states/", StateAPIView.as_view(), name="states"),
    path("franchise/", FranchiseAPIView.as_view(), name="franchise"),
    path("auth/", obtain_auth_token),

    path('authetication/', include('dj_rest_auth.urls')),
    path('user/', include('api.auth.urls')),
    path("pages/", include("api.pages.urls")),
    path("forms/", include("api.forms.urls")),
]
