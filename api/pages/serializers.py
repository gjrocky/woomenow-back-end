from rest_framework import serializers

from api.serializers import StreamFieldBlockSerializer, get_text
from apps.main.models import (
    FAQs, Business, About, Pricing,
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
    choose_image = serializers.SerializerMethodField(source="price_btn")
    CTA_btn = serializers.SerializerMethodField(source="CTA_btn")
    price_button = serializers.SerializerMethodField(source="price_btn")
    CTA_btn_icon = serializers.SerializerMethodField(source="CTA_btn_icon")

    def get_CTA_btn(self,obj):
        return get_text(obj.CTA_btn)

    def get_price_button(self, obj):
        return get_text(obj.price_btn)

    def get_choose_image(self, obj):
        try:
            return obj.choose_image.file.url
        except:
            return None

    def get_CTA_btn_icon(self, obj):
        try:
            return obj.CTA_btn_icon.file.url
        except:
            return None


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
            "choose_image",
            "win_plan_heading",
            "win_plan_description",
            "win_plan_cards",
            "why_choose_us_cards",
            "price_heading",
            "price_description",
            "price_button",
            "CTA_btn_icon",
            "faq",
            "key_point",
        ]


class AboutSerializer(serializers.ModelSerializer):
    cards = StreamFieldBlockSerializer(source="vision_points")

    class Meta:
        model = About
        fields = [
            "id",
            "title",
            "slug",
            "description",
            "heading",
            "vision_title",
            "image",
            "cards",
        ]


class PricingSerializer(serializers.ModelSerializer):
    pricing_cards = StreamFieldBlockSerializer(source="cards")

    class Meta:
        model = Pricing
        fields = [
            "id",
            "title",
            "slug",
            "heading",
            "description",
            'note',
            'CTA_btn',
            'pricing_cards'
        ]
