from rest_framework.generics import (
    ListAPIView,
)

from api.pages.serializers import FAQsSerializer, BusinessSerializer
from apps.main.models import FAQs, Business


class FAQsPageAPIViews(ListAPIView):
    queryset = FAQs.objects.live()
    serializer_class = FAQsSerializer


class BusinessAPIView(ListAPIView):
    pass
    queryset = Business.objects.live()
    serializer_class = BusinessSerializer
