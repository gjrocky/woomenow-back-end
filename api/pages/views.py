from rest_framework.generics import (
    RetrieveAPIView,
)

from api.pages.serializers import FAQsSerializer, BusinessSerializer, AboutSerializer, PricingSerializer, \
    JoinTheWooSerializer, InfluencerSerializer
from apps.main.models import FAQs, Business, About, Pricing, JoinTheWoo,Influencer


class FAQsPageAPIViews(RetrieveAPIView):
    queryset = FAQs.objects.live()
    serializer_class = FAQsSerializer

    def get_object(self):
        return self.get_queryset().first()


class BusinessPageAPIView(RetrieveAPIView):
    queryset = Business.objects.live()
    serializer_class = BusinessSerializer

    def get_object(self):
        return self.get_queryset().first()


class AboutPageAPIView(RetrieveAPIView):
    queryset = About.objects.live()
    serializer_class = AboutSerializer

    def get_object(self):
        return self.get_queryset().first()


class JoinTheWooPageAPIView(RetrieveAPIView):
    queryset = JoinTheWoo.objects.live()
    serializer_class = JoinTheWooSerializer

    def get_object(self):
        return self.get_queryset().first()


class PricingPageAPIView(RetrieveAPIView):
    queryset = Pricing.objects.live()
    serializer_class = PricingSerializer

    def get_object(self):
        return self.get_queryset().first()


class InfluencerPageAPIView(RetrieveAPIView):
    queryset = Influencer.objects.live()
    serializer_class = InfluencerSerializer
    lookup_field = 'pk'

    def get_object(self):
        return self.get_queryset().first()