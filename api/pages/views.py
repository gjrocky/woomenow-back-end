from rest_framework.generics import (
    ListAPIView,
)

from api.pages.serializers import FAQsSerializer, BusinessSerializer, AboutSerializer, PricingSerializer
from apps.main.models import FAQs, Business, About, Pricing


class FAQsPageAPIViews(ListAPIView):
    queryset = FAQs.objects.live()
    serializer_class = FAQsSerializer


class BusinessPageAPIView(ListAPIView):
    queryset = Business.objects.live()
    serializer_class = BusinessSerializer


class AboutPageAPIView(ListAPIView):
    queryset = About.objects.live()
    serializer_class = AboutSerializer


class PricingPageAPIView(ListAPIView):
    queryset = Pricing.objects.live()
    serializer_class = PricingSerializer
