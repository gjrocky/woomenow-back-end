from rest_framework import serializers

from api.serializers import StreamFieldBlockSerializer, get_text
from apps.main.models import Invitation, Review, Influencer
from apps.snippet.models import IPLocation, Contact, JoinTheWooForm, GiveOffer


class IPLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = IPLocation
        fields = "__all__"


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = "__all__"


class InvitationSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()

    def get_created_at(self, obj):
        return obj.created_at.strftime("%b %d, %Y")

    class Meta:
        model = Invitation
        fields = ['id', 'restaurant_name', 'created_at', 'location', 'invite_to', 'type', 'google_link']

    def create(self, validated_data):
        recommend_by = self.initial_data.get('recommend_by', {})
        influencer_id = recommend_by.get('value') if isinstance(recommend_by, dict) else None
        invited_by = Influencer.objects.filter(id=influencer_id).first()
        invitation = Invitation(**validated_data)
        if invited_by:
            invitation.invited_by = invited_by
        if self.initial_data.get('user'):
            invitation.super_user = self.initial_data.get('user')
        invitation.phone = self.initial_data.get('phone', None)
        invitation.save()
        return invitation


class JoinTheWooSerializer(serializers.ModelSerializer):
    class Meta:
        model = JoinTheWooForm
        fields = "__all__"


class ReviewSerializer(serializers.ModelSerializer):
    posted_by = serializers.SerializerMethodField(source='posted_by')
    restaurant = serializers.SerializerMethodField(source='restaurant')
    bill = serializers.SerializerMethodField(source='bill')
    images = StreamFieldBlockSerializer(required=False)
    created_at = serializers.SerializerMethodField()

    def get_posted_by(self, obj):
        try:
            influencer = obj.posted_by.influencer
            if influencer:
                return dict(
                    id=influencer.id,
                    name=get_text(influencer.name),
                    image=influencer.profile.file.url,
                    email=obj.posted_by.email,
                )
            return None
        except:
            try:
                profile = obj.posted_by.profile_picture.url or obj.posted_by.wagtail_userprofile.avatar.url
            except:
                profile = None
            return dict(
                id=obj.posted_by.id,
                name=f'{obj.posted_by.first_name} {obj.posted_by.last_name}',
                email=obj.posted_by.email,
                image=profile,
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

    def get_created_at(self, obj):
        return obj.created_at.strftime("%b %d, %Y")

    class Meta:
        model = Review
        fields = ['id', 'content', 'rating', 'is_verified', 'is_published', 'posted_by', 'bill', 'images', 'restaurant',
                  'more_info', 'created_at']


class GiveOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = GiveOffer
        fields = ["id", "review", "message", "goodwill_offer", "custom_offer", "created_at"]

    def validate(self, data):
        if data.get('goodwill_offer') == 'custom_offer' and not data.get('custom_offer'):
            raise serializers.ValidationError(
                {"custom_offer": "Custom offer text is required when goodwill_choice is 'custom'."}
            )
        return data
