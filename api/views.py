from rest_framework import status
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from api.serializers import CategorySerializer, StatesSerializer
from apps.snippet.models import Category, State


class CategoryAPIView(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class StateAPIView(ListAPIView):
    queryset = State.objects.all()
    serializer_class = StatesSerializer
