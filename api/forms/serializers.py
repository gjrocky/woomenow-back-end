from rest_framework import serializers

from api.serializers import StreamFieldBlockSerializer
from apps.main.models import Invitation, Review
from apps.snippet.models import IPLocation, Contact


class IPLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = IPLocation
        fields = "__all__"


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = "__all__"


class InvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invitation
        fields = "__all__"


class ReviewSerializer(serializers.ModelSerializer):
    posted_by = serializers.SerializerMethodField(source='posted_by')
    restaurant = serializers.SerializerMethodField(source='restaurant')
    bill = serializers.SerializerMethodField(source='bill')
    images = StreamFieldBlockSerializer(required=False)

    def get_posted_by(self, obj):
        try:
            profile = obj.posted_by.wagtail_userprofile.avatar.url
        except:
            profile = None
        return dict(
            id=obj.posted_by.id,
            name=obj.posted_by.full_name,
            email=obj.posted_by.email,
            profile=profile,
        )


    def get_bill(self, obj):
        try:
            bill = obj.bill.file.url
            return dict(url=bill, id=obj.bill.id)
        except:
            return dict()

    def get_restaurant(self, obj):
        try:
            return dict(
                name=obj.restaurant.name,
                id=obj.restaurant.id,
            )
        except:
            return dict()

    class Meta:
        model = Review
        fields = ['id', 'content', 'rating', 'is_verified', 'no_of_likes', 'posted_by', 'bill', 'images', 'restaurant']
