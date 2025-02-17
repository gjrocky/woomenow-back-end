from rest_framework import serializers

from api.helper import StreamFieldSerializer
from api.serializers import StreamFieldBlockSerializer, get_text, ImageSerializer
from apps.main.models import (
    FAQs, Business, About, Pricing, JoinTheWoo, Influencer,
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
    choose_image = serializers.SerializerMethodField(source="choose_image")
    CTA_btn = serializers.SerializerMethodField(source="CTA_btn")
    price_button = serializers.SerializerMethodField(source="price_btn")
    CTA_btn_icon = serializers.SerializerMethodField(source="CTA_btn_icon")

    def get_CTA_btn(self, obj):
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


class JoinTheWooSerializer(serializers.ModelSerializer):
    Points = StreamFieldBlockSerializer(source="community_points")

    class Meta:
        model = JoinTheWoo
        fields = [
            "id",
            "title",
            "slug",
            "heading",
            "description",
            "about_community",
            "sub_heading",
            "Points",
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


class InfluencerSerializer(serializers.ModelSerializer):
    city = serializers.SerializerMethodField(source='city')
    profile_image = serializers.SerializerMethodField(source='profile')
    restaurant_images = StreamFieldSerializer()
    social_links = StreamFieldSerializer()

    def get_city(self, obj):
        return dict(
            name=obj.city.name,
            slug=obj.city.slug,
            state=dict(
                name=obj.city.state.name,
                slug=obj.city.state.slug,
                ISO_code=obj.city.state.ISO_code,
            )
        )

    def get_profile_image(self, obj):
        try:
            return obj.profile.file.url
        except:
            return None

    class Meta:
        model = Influencer

        fields = ['id', 'title', 'slug', 'name', 'description', 'city', 'profile_image', 'restaurant_images',
                  'social_links']
