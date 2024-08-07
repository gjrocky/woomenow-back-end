from rest_framework import serializers

from api.serializers import StreamFieldBlockSerializer, get_text
from apps.main.models import (
    FAQs, Business,
)


class FAQsSerializer(serializers.ModelSerializer):
    faqs = StreamFieldBlockSerializer(source="faq")

    class Meta:
        model = FAQs
        fields = ["id", "title", "slug", "faqs"]


class BusinessSerializer(serializers.ModelSerializer):
    key_point = StreamFieldBlockSerializer()
    why_choose_us_cards = StreamFieldBlockSerializer()
    win_plan_cards = StreamFieldBlockSerializer()
    faq = StreamFieldBlockSerializer()
    price_button = serializers.SerializerMethodField(source="price_btn")
    heading = serializers.SerializerMethodField(source="heading")
    description = serializers.SerializerMethodField(source="description")

    def get_heading(self, obj):
        return get_text(obj.heading)

    def get_description(self, obj):
        return get_text(obj.description)

    def get_price_button(self, obj):
        return get_text(obj.price_btn)

    class Meta:
        model = Business
        fields = [
            "id",
            "title",
            "slug",
            "CTA_btn",
            "heading",
            "description",
            "video_1",
            "video_2",
            "video_3",
            "choose_heading",
            "choose_description",
            "win_plan_heading",
            "win_plan_description",
            "win_plan_cards",
            "why_choose_us_cards",
            "price_heading",
            "price_description",
            "price_button",
            "CTA_btn_icon",
            "choose_image",
            "faq",
            "key_point",
        ]
