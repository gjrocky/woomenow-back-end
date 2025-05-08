import json

from bs4 import BeautifulSoup
from django.conf import settings
from django.db.models import Q
from pywebpush import webpush, WebPushException
from rest_framework import permissions, status
from rest_framework.authentication import SessionAuthentication
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from wagtail.images.models import Image

from api.pages.serializers import RestaurantListSerializer
from api.serializers import CategorySerializer, StatesSerializer, FranchiseSerializer, StatesInfluencerSerializer, \
    CitiesSerializer, AmbienceSerializer, ReviewSerializer
from apps.main.models import Franchise, Restaurant, Review, NotificationPermission, NotificationHistory
from apps.snippet.models import Category, State, City, Ambience


class CategoryAPIView(ListAPIView):
    serializer_class = CategorySerializer

    def get_queryset(self):
        categories = Category.objects.all()
        city = self.request.query_params.get('city')
        type = self.request.query_params.get('type')
        if city:
            categories = categories.filter(Restaurants__city__slug=city).distinct()
        else:
            city = City.objects.first()
            categories = categories.filter(Restaurants__city__slug=city.slug).distinct()

        if type:
            categories = categories.filter(Restaurants__type=type).distinct()
        return categories


class StateAPIView(ListAPIView):
    queryset = State.objects.all()
    serializer_class = StatesSerializer


class CityAPIView(ListAPIView):
    serializer_class = CitiesSerializer
    queryset = City.objects.all()


class FranchiseAPIView(ListAPIView):
    queryset = Franchise.objects.all()
    serializer_class = FranchiseSerializer


class StateInfluencerAPIView(ListAPIView):
    serializer_class = StatesInfluencerSerializer
    queryset = State.objects.all()


class AmbienceAPIView(ListAPIView):
    queryset = Ambience.objects.all()
    serializer_class = AmbienceSerializer

    def get_queryset(self):
        queryset = self.queryset.all()
        type = self.request.query_params.get("type")
        r_id = self.request.query_params.get("restaurant")
        city = self.request.query_params.get("city")

        if r_id:
            return queryset.filter(Restaurants__id=r_id).distinct()

        if city:
            queryset = queryset.filter(Restaurants__city__slug=city).distinct()
        else:
            city = City.objects.first()
            queryset = queryset.filter(Restaurants__city=city).distinct()
        if type:
            queryset = queryset.filter(Restaurants__type=type).distinct()

        return queryset


class RecommendationAPIView(ListAPIView):
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantListSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset.filter(recommended_by=user)
        return queryset


class ReviewAPIView(ListAPIView):
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset.filter(posted_by=user)
        return queryset


class NotificationAPIView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        endpoint = data.get('endpoint')
        p256dh = data.get('keys', {}).get('p256dh')
        auth = data.get('keys', {}).get('auth')
        try:
            NotificationPermission.objects.get(endpoint=endpoint)
            return Response({'success': 'Notification Permission Updated'}, status=status.HTTP_200_OK)
        except NotificationPermission.DoesNotExist:
            permission = NotificationPermission(endpoint=endpoint, p256dh=p256dh, auth=auth)
            if request.user.is_authenticated:
                permission.user = request.user
            permission.save()
            return Response({'success': 'Notification Permission Created'}, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        NotificationPermission.objects.filter(user=request.user).delete()
        return Response({'success': 'Notification Permission Deleted'}, status=status.HTTP_200_OK)


class SendNotificationAPIView(APIView):
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response({'error': 'Permission Denied'}, status=status.HTTP_403_FORBIDDEN)

        data = request.data
        title = data.get('title')
        description = data.get('description')
        send_to = data.get('send_to', []) or data.getlist('send_to[]')
        img = data.get('files[]')
        notification_history = NotificationHistory(title=title, description=description, send_to=send_to)
        if img:
            wagtail_image = Image.objects.create(title=img.name, file=img)
            notification_history.image = wagtail_image
        notification_history.save()
        send_push_notification(title, description, send_to, notification_history)
        return Response({'success': 'Notification Sent'}, status=status.HTTP_200_OK)


def send_push_notification(title, message, send_to, notification_history):
    filters = Q()
    if 'admin' in send_to:
        filters = filters | Q(user__is_superuser=True)
    if 'restaurant' in send_to:
        filters = filters | Q(user__restaurants__isnull=False)
    if 'influencer' in send_to:
        filters = filters | Q(user__influencer__isnull=False)
    if 'user' in send_to:
        filters = filters | Q(user__isnull=False)
    if 'everyone' in send_to:
        filters = Q()

    subscriptions = NotificationPermission.objects.filter(filters).distinct()

    for subscription in subscriptions:
        try:
            response = webpush(
                subscription_info={
                    'endpoint': subscription.endpoint,  # The URL of the push service
                    'keys': {
                        'p256dh': subscription.p256dh,  # The encryption key
                        'auth': subscription.auth  # The authentication key
                    }
                },
                data=json.dumps({
                    'head': title,
                    'body': BeautifulSoup(message, "html.parser").get_text(),
                    "image": notification_history.image.file.url if notification_history.image else None,
                }),
                vapid_private_key=settings.VAPID_PRIVATE_KEY,  # Your VAPID private key here
                vapid_claims={'sub': f'mailto:{settings.ADMIN_EMAIL}'}
            )
        except WebPushException as e:
            print(f"Error sending push notification: {e}")
