from woo_me_now_backend.validator import CustomPasswordValidator
from django.core.exceptions import ValidationError
from rest_framework import serializers
from wagtail.images.models import Image


def password_checker(password):
    try:
        validator = CustomPasswordValidator()
        validator.validate(password)
        return password, False
    except ValidationError as e:
        return ', '.join(e.messages), True


class StreamFieldSerializer(serializers.Field):
    def to_representation(self, value):
        """Convert StreamField value to a JSON-serializable format."""
        if not value:
            return []

        result = []
        for block in value:  # StreamField behaves like a list
            if block.block_type == 'image':  # Ensure it's an image block
                image_id = block.value.id  # Get Image ID
                try:
                    image = Image.objects.get(id=image_id)  # Fetch Image
                    result.append({
                        "type": "image",
                        "id": image.id,
                        "url": image.file.url,  # Get Image URL
                    })
                except Image.DoesNotExist:
                    result.append({
                        "type": "image",
                        "id": image_id,
                        "url": None,
                    })
            else:
                result.append({
                    "type": block.block_type,
                    "value": block.value,  # Other non-image values
                    "id": block.id,
                })

        return result  # Returns a JSON-compatible format

    def to_internal_value(self, data):
        print(data)
        """Convert JSON data back into StreamField format."""
        return data  # Assumes data is already in correct format


def city(obj):
    return dict(
        name=obj.city.name,
        slug=obj.city.slug,
        state=dict(
            name=obj.city.state.name,
            slug=obj.city.state.slug,
            ISO_code=obj.city.state.ISO_code,
        )
    )
