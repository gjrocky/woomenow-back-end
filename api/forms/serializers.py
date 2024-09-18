from rest_framework import serializers

from apps.snippet.models import IPLocation, Contact


class IPLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = IPLocation
        fields = "__all__"


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = "__all__"

# class DynamicFormSerializer(serializers.Serializer):
#     def __init__(self, *args, **kwargs):
#         form_page = kwargs.pop("form_page")
#         super().__init__(*args, **kwargs)
#
#         for field in form_page.form_fields.all():
#             field_name = field.clean_name
#             field_type = field.field_type
#
#             if field_type == "singleline":
#                 self.fields[field_name] = serializers.CharField()
#             elif field_type == "multiline":
#                 self.fields[field_name] = serializers.CharField(
#                     style={"base_template": "textarea.html"}
#                 )
#             elif field_type == "email":
#                 self.fields[field_name] = serializers.EmailField()
#             elif field_type == "number":
#                 self.fields[field_name] = serializers.IntegerField()
#             elif field_type == "url":
#                 self.fields[field_name] = serializers.URLField()