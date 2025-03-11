from rest_framework import permissions
from rest_framework.authentication import SessionAuthentication
from rest_framework.generics import ListAPIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenObtainPairView

from api.pages.serializers import RestaurantListSerializer
from api.serializers import CategorySerializer, StatesSerializer, FranchiseSerializer, StatesInfluencerSerializer, \
    CitiesSerializer, AmbienceSerializer, ReviewSerializer, CustomTokenObtainPairSerializer
from apps.main.models import Franchise, Restaurant, Review
from apps.snippet.models import Category, State, City, Ambience


class CategoryAPIView(ListAPIView):
    serializer_class = CategorySerializer

    def get_queryset(self):
        categories = Category.objects.all()
        city = self.request.query_params.get('city')
        type = self.request.query_params.get('type')
        if city:
            categories = categories.filter(Restaurants__city__slug=city).distinct()
        else:
            city = City.objects.first()
            categories = categories.filter(Restaurants__city__slug=city.slug).distinct()

        if type:
            categories = categories.filter(Restaurants__type=type).distinct()
        return categories


class StateAPIView(ListAPIView):
    queryset = State.objects.all()
    serializer_class = StatesSerializer


class CityAPIView(ListAPIView):
    serializer_class = CitiesSerializer
    queryset = City.objects.all()


class FranchiseAPIView(ListAPIView):
    queryset = Franchise.objects.all()
    serializer_class = FranchiseSerializer


class StateInfluencerAPIView(ListAPIView):
    serializer_class = StatesInfluencerSerializer
    queryset = State.objects.all()


class AmbienceAPIView(ListAPIView):
    queryset = Ambience.objects.all()
    serializer_class = AmbienceSerializer

    def get_queryset(self):
        queryset = self.queryset.all()
        type = self.request.query_params.get("type")
        r_id = self.request.query_params.get("restaurant")
        city = self.request.query_params.get("city")

        if r_id:
            return queryset.filter(Restaurants__id=r_id).distinct()

        if city:
            queryset = queryset.filter(Restaurants__city__slug=city).distinct()
        else:
            city = City.objects.first()
            queryset = queryset.filter(Restaurants__city=city).distinct()
        if type:
            queryset = queryset.filter(Restaurants__type=type).distinct()

        return queryset


class RecommendationAPIView(ListAPIView):
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantListSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset.filter(recommended_by=user)
        return queryset


class ReviewAPIView(ListAPIView):
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset.filter(posted_by=user)
        return queryset