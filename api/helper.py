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


class OrderedStreamFieldSerializer(serializers.Field):
    def to_representation(self, value):
        """Convert StreamField value to a JSON-serializable format."""
        if not value:
            return []

        result = []
        for block in value:  # StreamField behaves like a list
            if block.block_type == 'image':
                image_id = block.value.id
                try:
                    image = Image.objects.get(id=image_id)
                    result.append({
                        "type": "image",
                        "id": image.id,
                        "url": image.file.url,
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
                    "value": block.value,
                    "id": block.id,
                })

        # ✅ Sort image blocks by ID, keep non-image blocks at the end
        sorted_result = sorted(
            result,
            key=lambda x: (0, x["id"]) if x["type"] == "image" else (1, 0)
        )
        return sorted_result


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
