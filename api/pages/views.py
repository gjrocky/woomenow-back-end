from rest_framework.generics import (
    ListAPIView,
)

from api.pages.serializers import FAQsSerializer
from apps.main.models import FAQs


class FAQsPageAPIViews(ListAPIView):
    queryset = FAQs.objects.live()
    serializer_class = FAQsSerializer