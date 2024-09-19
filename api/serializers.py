from bs4 import BeautifulSoup
from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
from wagtail.blocks import StreamValue
from wagtail.fields import StreamField
from wagtail.images.models import Image
from wagtail.rich_text import RichText
from apps.main.blocks import PricingCard
from apps.main.models import Franchise
from apps.snippet.models import Category, State


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            "id",
            "name",
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
    page_size = 9


class ImageSerializer(serializers.Serializer):
    id = serializers.IntegerField(source="value.id")
    url = serializers.SerializerMethodField()
    name = serializers.CharField(source="value.title")

    def get_url(self, obj):
        return obj.value.file.url


def get_text(text):
    return BeautifulSoup(text, "html.parser").get_text()
