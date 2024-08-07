from rest_framework import serializers

from api.serializers import StreamFieldBlockSerializer
from apps.main.models import (
    FAQs,
)


class FAQsSerializer(serializers.ModelSerializer):
    faqs = StreamFieldBlockSerializer(source="faq")

    class Meta:
        model = FAQs
        fields = ["id", "title", "slug", "faqs"]
