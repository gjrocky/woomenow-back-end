from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
from wagtail.blocks import StreamValue
from wagtail.images.models import Image
from wagtail.rich_text import RichText
from bs4 import BeautifulSoup


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
            return dict(info=BeautifulSoup(block.__html__(), 'html.parser').get_text())
        else:
            return dict(name=block)

    def struct_block(self, block):
        data = dict()
        for field_name, field_value in block.items():
            if isinstance(field_value, Image):
                data[field_name] = field_value.file.url
            elif isinstance(field_value, RichText):
                data[field_name] = BeautifulSoup(field_value.__html__(), 'html.parser').get_text()
            elif isinstance(field_value, StreamValue):
                data[field_name] = [self.serialize_block(value.value) for value in field_value]
            else:
                data[field_name] = field_value
        return data



class ImageSerializer(serializers.Serializer):
    id = serializers.IntegerField(source="value.id")
    url = serializers.SerializerMethodField()
    name = serializers.CharField(source="value.title")

    def get_url(self, obj):
        return obj.value.file.url


class Pagination(PageNumberPagination):
    page_size = 9


def get_text(text):
    return BeautifulSoup(text, "html.parser").get_text()
