from rest_framework.generics import ListAPIView

from api.serializers import CategorySerializer, StatesSerializer, FranchiseSerializer
from apps.main.models import Franchise
from apps.snippet.models import Category, State, City


class CategoryAPIView(ListAPIView):
    serializer_class = CategorySerializer

    def get_queryset(self):
        categories = Category.objects.all()
        city = self.request.query_params.get('city')
        if city:
            categories = categories.filter(Restaurants__city__slug=city)
        else:
            city = City.objects.first()
            categories = categories.filter(Restaurants__city__slug=city.slug)
        return categories


class StateAPIView(ListAPIView):
    queryset = State.objects.all()
    serializer_class = StatesSerializer


class FranchiseAPIView(ListAPIView):
    queryset = Franchise.objects.all()
    serializer_class = FranchiseSerializer
