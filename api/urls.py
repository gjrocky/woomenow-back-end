from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

from api.views import StateAPIView, CategoryAPIView, FranchiseAPIView, StateInfluencerAPIView, CityAPIView, \
    AmbienceAPIView, RecommendationAPIView, ReviewAPIView, NotificationAPIView, SendNotificationAPIView

app_name = "api"

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path("categories/", CategoryAPIView.as_view(), name="categories"),
    path("states/", StateAPIView.as_view(), name="states"),
    path("cities/", CityAPIView.as_view(), name="cities"),
    path("franchise/", FranchiseAPIView.as_view(), name="franchise"),
    path("state-influencers/", StateInfluencerAPIView.as_view(), name="state-influencers"),
    path("ambience/", AmbienceAPIView.as_view(), name="ambience"),
    path("recommendation/", RecommendationAPIView.as_view(), name="recommendation"),
    path("reviews/", ReviewAPIView.as_view(), name="reviews"),
    path('notification/', NotificationAPIView.as_view(), name='notification'),
    path('send-notification/', SendNotificationAPIView.as_view(), name='send-notification'),
    path("auth/", obtain_auth_token),

    path('authetication/', include('dj_rest_auth.urls')),
    path('user/', include('api.auth.urls')),
    path("pages/", include("api.pages.urls")),
    path("forms/", include("api.forms.urls")),
]
