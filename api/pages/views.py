from rest_framework.generics import (
    ListAPIView,
)

from api.pages.serializers import FAQsSerializer, BusinessSerializer, AboutSerializer
from apps.main.models import FAQs, Business, About


class FAQsPageAPIViews(ListAPIView):
    queryset = FAQs.objects.live()
    serializer_class = FAQsSerializer


class BusinessPageAPIView(ListAPIView):
    queryset = Business.objects.live()
    serializer_class = BusinessSerializer


class AboutPageAPIView(ListAPIView):
    queryset = About.objects.live()
    serializer_class = AboutSerializer
