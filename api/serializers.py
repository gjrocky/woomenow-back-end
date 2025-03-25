from bs4 import BeautifulSoup
from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from wagtail.blocks import StreamValue
from wagtail.fields import StreamField
from wagtail.images.models import Image
from wagtail.rich_text import RichText

from apps.main.blocks import PricingCard
from apps.main.models import Franchise, Review
from apps.snippet.models import Category, State, City, Ambience
from apps.users.models import User


class CategorySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField(source="image")

    def get_image(self, obj):
        try:
            return obj.image.file.url
        except:
            return None

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "image"
        ]


class StatesSerializer(serializers.ModelSerializer):
    cities = serializers.SerializerMethodField()

    def get_cities(self, obj):
        return [
            dict(
                name=city.name,
                slug=city.slug,
                locality=[
                    dict(
                        name=loc.name,
                        slug=loc.slug
                    ) for loc in city.Localities.all()],
            )
            for city in obj.cities.all()
        ]

    class Meta:
        model = State
        fields = ["id", "name", "slug", "ISO_code", "cities"]


class CitiesSerializer(serializers.ModelSerializer):
    state = serializers.SerializerMethodField(source="state")

    def get_state(self, obj):
        return dict(
            name=obj.state.name,
            slug=obj.state.slug,
            ISO_code=obj.state.ISO_code,
        )

    class Meta:
        model = City
        fields = ["id", "name", "slug", "state"]


class StatesInfluencerSerializer(serializers.ModelSerializer):
    cities = serializers.SerializerMethodField()

    def get_cities(self, obj):
        return [
            dict(
                name=city.name,
                slug=city.slug,
                influencer_count=city.influencers.count(),
                dining=city.Restaurants.filter(type='dining').count(),
                experience=city.Restaurants.filter(type='experience').count(),
                locality=[
                    dict(
                        name=loc.name,
                        slug=loc.slug
                    ) for loc in city.Localities.all()],
            )
            for city in obj.cities.all()
        ]

    class Meta:
        model = State
        fields = ["id", "name", "slug", "ISO_code", "cities"]


class StreamFieldBlockSerializer(serializers.Field):
    def to_representation(self, value):
        return self.serialize_streamfield(value)

    def serialize_streamfield(self, streamfield):
        return [self.serialize_block(block.value) for block in streamfield]

    def serialize_block(self, block):
        if isinstance(block, dict):
            return self.struct_block(block)
        elif isinstance(block, Image):
            return dict(url=block.file.url)
        elif isinstance(block, RichText):
            return dict(info=block.__html__())
        else:
            return dict(name=block)

    def struct_block(self, block):
        data = dict()
        for field_name, field_value in block.items():
            if isinstance(field_value, Image):
                data[field_name] = field_value.file.url
            elif isinstance(field_value, RichText):
                data[field_name] = field_value.__html__()
            elif isinstance(field_value, StreamValue):
                data[field_name] = [self.serialize_block(value.value) for value in field_value]
            else:
                data[field_name] = field_value
        return data

    def to_internal_value(self, data):
        stream_field = StreamField(PricingCard())
        return stream_field.stream_block.get_prep_value(data)


class FranchiseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Franchise
        fields = '__all__'


class Pagination(PageNumberPagination):
    page_size = 1
    page_size_query_param = 'page_size'


class ImageSerializer(serializers.Serializer):
    id = serializers.IntegerField(source="value.id")
    url = serializers.SerializerMethodField()
    name = serializers.CharField(source="value.title")

    def get_url(self, obj):
        return obj.value.file.url


class AmbienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ambience
        fields = ['id', 'name']


def get_text(text):
    return BeautifulSoup(text, "html.parser").get_text()


class ReviewSerializer(serializers.ModelSerializer):
    restaurant = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    bill = serializers.SerializerMethodField()

    def get_bill(self, obj):
        try:
            return obj.bill.file.url
        except:
            return None

    def get_user(self, obj):
        return f'{obj.posted_by.first_name} {obj.posted_by.last_name}'

    def get_restaurant(self, obj):
        try:
            image = obj.restaurant.restaurant_images[0].value.file.url
        except:
            image = None
        return dict(
            name=get_text(obj.restaurant.name),
            id=obj.restaurant.id,
            slug=obj.restaurant.slug,
            image=image,
        )

    def get_created_at(self, obj):
        return obj.created_at.strftime("%b %d, %Y")

    class Meta:
        model = Review
        fields = ['id', 'content', 'is_verified', 'bill', 'is_published', 'more_info', 'rating', 'created_at',
                  'restaurant', 'user']


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email  # Add email to JWT payload
        return token

    def validate(self, attrs):
        email = attrs.get("email")
        get_object_or_404(User, email=email)
        return super().validate(attrs)
