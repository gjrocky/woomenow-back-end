from rest_framework.generics import ListAPIView, ListCreateAPIView

from api.serializers import CategorySerializer, StatesSerializer, FranchiseSerializer
from apps.main.models import Franchise
from apps.snippet.models import Category, State


class CategoryAPIView(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class StateAPIView(ListAPIView):
    queryset = State.objects.all()
    serializer_class = StatesSerializer


class FranchiseAPIView(ListAPIView):
    queryset = Franchise.objects.all()
    serializer_class = FranchiseSerializer


