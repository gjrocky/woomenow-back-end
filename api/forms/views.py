from datetime import datetime

import requests
from bs4 import BeautifulSoup
from django.conf import settings
from django.db.models import Q
from django.http.request import QueryDict
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import permissions
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.generics import CreateAPIView, ListCreateAPIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from wagtail.images.models import Image

from api.constants import QUERY_PARAMS
from api.forms.serializers import IPLocationSerializer, ContactSerializer, InvitationSerializer, ReviewSerializer, \
    JoinTheWooSerializer
from api.serializers import Pagination
from api.serializers import ReviewSerializer as RSerializer
from apps.main.helper import email_dict
from apps.main.models import Invitation, Review, Restaurant, BecomeInfluencer, Influencer
from apps.snippet.models import IPLocation, Contact, JoinTheWooForm, City, Campaign, CampaignTracker
from send_email import send_email

api_counter = 0
send_email_counter = {}


def get_text(text):
    return BeautifulSoup(text, "html.parser").get_text()


def get_location(ip_add):
    global api_counter
    ip_address = ip_add
    try:
        api_key = settings.BIG_DATA_CLOUD_API_KEYS[
            api_counter % len(settings.BIG_DATA_CLOUD_API_KEYS)
            ]
        response = requests.get(
            f"https://api-bdc.net/data/ip-geolocation?ip={ip_address}&key={api_key}"
        ).json()

        api_counter += 1
        if api_counter == len(settings.BIG_DATA_CLOUD_API_KEYS):
            api_counter = 0

    except Exception:
        response = {}
    return {
        "location": response.get("location", dict()),
        "country": response.get("country", dict()),
    }


def create_update_ip(ip, ip_data):
    res = get_location(ip)
    if not ip_data:
        ip_data = IPLocation.objects.create(ip_address=ip)
    ip_data.city = res.get("location", {}).get("city", "")
    ip_data.state = res.get("location", {}).get("principalSubdivision", "")
    ip_data.country = res.get("country", {}).get("name", "")
    ip_data.ISO = (
        res.get("location", {}).get("isoPrincipalSubdivisionCode", "").split("-")[-1]
    )
    ip_data.extra = res
    ip_data.save()
    return ip_data


def get_ip_object(ip):
    try:
        ip_data = IPLocation.objects.get(ip_address=ip)
        days_ago = timezone.now() - timezone.timedelta(days=settings.RESET_DAYS)
        if ip_data.modified_at > days_ago:
            return ip_data, ip
        else:
            data = create_update_ip(ip, ip_data)
            return data, ip
    except IPLocation.DoesNotExist:
        data = create_update_ip(ip, None)
        return data, ip


class IPLocationAPIView(APIView):
    queryset = IPLocation.objects.all()
    serializer_class = IPLocationSerializer

    def post(self, request, *args, **kwargs):
        ip = request.data.get('ip')
        if ip:
            data, ip = get_ip_object(ip)
            city_name = data.city if data.city else None
        else:
            city_name = None

        try:
            location = City.objects.get(name=city_name).slug if city_name else City.objects.first().slug
        except City.DoesNotExist:
            location = City.objects.first().slug

        return Response({'location': location}, status=status.HTTP_200_OK)


class ContactAPIView(CreateAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer

    def perform_create(self, serializer):
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class JoinTheWooAPIView(CreateAPIView):
    queryset = JoinTheWooForm.objects.all()
    serializer_class = JoinTheWooSerializer

    def perform_create(self, serializer):
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class InvitationAPIView(ListCreateAPIView):
    queryset = Invitation.objects.all()
    serializer_class = InvitationSerializer

    def perform_create(self, serializer):
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class BookmarkAPIView(APIView):
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return Response({"error": "User not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            restaurant = Restaurant.objects.get(id=request.data['id'])
            if restaurant in user.Restaurants.all():
                user.Restaurants.remove(restaurant)
                user.point = user.point - 1 if user.point > 0 else 0
                user.save()
                return Response({"message": "Bookmark removed successfully"}, status=status.HTTP_200_OK)
            user.Restaurants.add(restaurant)
            user.point = user.point + 1
            user.save()

            return Response({"message": "Bookmark added successfully", 'added': True}, status=status.HTTP_200_OK)
        except Restaurant.DoesNotExist:
            return Response({"error": "Restaurant not found"}, status=status.HTTP_404_NOT_FOUND)


@extend_schema(
    parameters=[
        # OpenApiParameter(
        #     name="user", description="User ID", required=False, type=int
        # ),
        OpenApiParameter(
            name="restaurant", description="Restaurant ID", required=False, type=int
        )
    ]
)
class ReviewAPIView(APIView):

    def get(self, request, *args, **kwargs):
        filter_query = Q()
        restaurant_slug = self.request.query_params.get(
            QUERY_PARAMS["restaurant"]
        )
        sort = self.request.query_params.get('sort', 'Newest')
        is_paginate = self.request.query_params.get("is_pagination", 'false') == 'true'

        reviews = Review.objects.filter(restaurant__slug=restaurant_slug, is_published=True)
        thumb_up = 0
        heart = 0
        diamond = 0
        for review in reviews:
            if review.rating >= 4:
                diamond += 1
            elif review.rating < 3.5:
                thumb_up += 1
            else:
                heart += 1
        extra_info = dict(no_of_reviews=reviews.count(),
                          no_of_likes=dict(diamond=diamond, heart=heart, thumb_up=thumb_up))

        filter_type = dict(heart='heart', diamond='diamond', thumb_up='thumb_up')
        filter = self.request.query_params.get('filter')
        limit = self.request.query_params.get('limit', None)
        if filter and filter == filter_type['diamond']:
            filter_query &= Q(rating__gte=4)
        elif filter and filter == filter_type['heart']:
            filter_query &= (Q(rating__gte=3.5) & Q(rating__lt=4))
        elif filter and filter == filter_type['thumb_up']:
            filter_query &= Q(rating__lt=3.5)

        reviews = reviews.filter(filter_query).order_by('-created_at' if sort == 'Newest' else 'created_at')
        if limit:
            reviews = reviews[:int(limit)]
        if is_paginate:
            paginator = Pagination()
            page = paginator.paginate_queryset(reviews, request, view=self)

            total_pages = (paginator.page.paginator.count // paginator.page_size) + (
                1 if paginator.page.paginator.count % paginator.page_size > 0 else 0)

            serializer = ReviewSerializer(page, many=True)
            response_data = paginator.get_paginated_response(serializer.data).data
            response_data['total_pages'] = total_pages
        else:
            serializer = ReviewSerializer(reviews, many=True)
            response_data = serializer.data
        if reviews:
            return Response({'data': response_data, **extra_info}, status=200)
        else:
            return Response({'data': [], **extra_info}, status=200)


class ReviewPostAPIView(APIView):
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser,)

    def send_influencer_emails(self, review, res, email_dict):
        global send_email_counter
        cities = City.objects.values_list('name', flat=True)

        for city in cities:
            if not send_email_counter.get(city):
                send_email_counter[city] = 0

        influencers = Influencer.objects.filter(city=res.city)

        if not influencers.exists():
            return

        influencer = influencers[send_email_counter[res.city.name] % influencers.count()]
        e = [influencer.user.email]
        body = 'emails/receive-review-for-approval-influencer.html'
        context = dict(
            name=get_text(influencer.name),
            res_name=get_text(res.name),
            date=review.created_at.strftime("%b %d, %Y"),
            rating=review.rating,
            summary=review.content,
            **email_dict
        )
        subject_context = dict(subject='New Review Awaiting Your Approval.')
        send_email_counter[res.city.name] = send_email_counter[res.city.name] + 1
        send_email(e, body, context, subject_context)

    def post(self, request, *args, **kwargs):
        data = QueryDict('', mutable=True)
        for key, value_list in request.data.lists():
            for value in value_list:
                data.update({key: value})
        bill = request.data.get('file[]', None)

        rating_data = dict(
            recommended=data.get('recommended'),
            dish=data.get('dish'),
            cleanliness=data.get('cleanliness'),
            service=data.get('service'),
            food=data.get('food'),
            ambience=data.get('ambience')
        )
        count = 0

        if not request.data.get('res_id'):
            return Response({'error': 'Provide the restaurant ID'}, status=status.HTTP_400_BAD_REQUEST)

        json_data = dict(vibe=data.get('aura[]'), dish=data.get('dish'), cleanliness=data.get('cleanliness'),
                         service=data.get('service'), food=data.get('food'), ambience=data.get('ambience'))

        total_rating = 0
        for key, value in rating_data.items():
            if value:
                count += 1
                total_rating += int(value) or 0

        if total_rating > 0:
            total_rating = round(total_rating / count, 2)

        review = Review(posted_by=request.user, content=data.get('message'),
                        rating=total_rating,
                        restaurant_id=request.data.get('res_id'), more_info=json_data, created_at=datetime.now())

        if bill:
            wagtail_image = Image.objects.create(title=bill.name, file=bill)
            review.bill = wagtail_image

        review.save()
        try:
            res = Restaurant.objects.get(id=request.data.get('res_id'))
            # threading.Thread(target=self.send_influencer_emails, args=(review, res, email_dict)).start()

            return Response({'message': 'Your review has been published after verification.'},
                            status=status.HTTP_201_CREATED)
        except Restaurant.DoesNotExist:
            return Response({'error': 'Provided the Restaurant ID does not exist'}, status=status.HTTP_404_NOT_FOUND)


class PendingReviewAPIView(APIView):
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = Review.objects.all()
    serializer_class = RSerializer

    def get(self, request, *args, **kwargs):
        queryset = self.queryset.filter(is_verified=False)[:10]
        serializer = self.serializer_class(queryset, many=True)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        id = data.get('id')
        is_approved = data.get('is_approved', None)
        if not id:
            return Response({'error': 'Provide the Review ID'}, status=status.HTTP_400_BAD_REQUEST)

        if is_approved == None:
            return Response({'error': 'Provide the proper data'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            queryset = self.queryset.get(id=id)
            queryset.is_published = is_approved
            queryset.is_verified = True
            queryset.save()
            return Response({'message': 'Review is Updated'}, status=status.HTTP_200_OK)

        except Review.DoesNotExist:
            return Response({'error': 'Provided the Review ID does not exist'}, status=status.HTTP_404_NOT_FOUND)


class BecomeAnInfluencerAPIView(APIView):
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        insta = request.data.get('instagram')
        tiktok = request.data.get('tiktok')
        other = request.data.get('other')

        if not insta and not tiktok and not other:
            return Response({'error': 'Provide social media link'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            becomeAnInfluencer = BecomeInfluencer(user=user, insta_link=insta, tiktok_link=tiktok, other_link=other)
            becomeAnInfluencer.save()

            return Response({'message': 'Your request to become an influencer has been submitted.'},
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': 'you already requested'}, status=status.HTTP_400_BAD_REQUEST)


class RestaurantInvitationAPIView(APIView):
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        try:
            influ = user.influencer
            queryset = Invitation.objects.filter(invited_by=influ)
            serializer = InvitationSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            if user.is_superuser:
                queryset = Invitation.objects.filter(super_user=user)
                serializer = InvitationSerializer(queryset, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'You are not authorized to view this data'},
                                status=status.HTTP_401_UNAUTHORIZED)

    def post(self, request, *args, **kwargs):
        user = request.user
        try:
            influ = user.influencer
            serializer = InvitationSerializer(data={'influ_id': influ.id, **request.data})
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                e = [request.data.get('invite_to')]
                body = 'emails/exp-get-an-email-to-onboard.html'
                context = dict(name=request.data.get('restaurant_name'), **email_dict)
                subject_context = dict(subject='Congratulations! You’re Now Part of WooMeNow.')
                send_email(e, body, context, subject_context)
                return Response({'message': 'Our team will the check & verify the restaurant/experience'},
                                status=status.HTTP_201_CREATED)
        except Exception as e:
            serializer = InvitationSerializer(data={**request.data, "user": user})
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                e = [request.data.get('invite_to')]
                body = 'emails/exp-get-an-email-to-onboard.html'
                context = dict(name=request.data.get('restaurant_name'), **email_dict)
                subject_context = dict(subject='Congratulations! You’re Now Part of WooMeNow.')
                send_email(e, body, context, subject_context)
                return Response({'message': 'Our team will the check & verify the restaurant/experience'},
                                status=status.HTTP_201_CREATED)


class CampaignAPIView(APIView):
    queryset = Campaign.objects.all()
    lookup_field = 'slug'

    def get(self, request, *args, **kwargs):
        try:
            campaign = self.queryset.get(slug=kwargs.get('slug'), is_active=True)
            ip = request.query_params.get('ip')
            location_data, ip = get_ip_object(ip)
            try:
                CampaignTracker.objects.get(Q(ip=ip) & Q(campaign=campaign))
            except CampaignTracker.DoesNotExist:
                user = CampaignTracker.objects.create(ip=ip)
                user.user_device = request.META.get("HTTP_USER_AGENT")
                user.redirect_to = request.path
                user.location = f"{location_data.city} - {location_data.state} - {location_data.country}"
                user.extra_data = {
                    "utm_source": campaign.utm_source,
                    "utm_medium": campaign.utm_medium,
                    "utm_campaign": campaign.utm_campaign,
                }
                user.campaign = campaign
                user.save()
            return Response({"redirect_to": campaign.redirect_to}, status=status.HTTP_200_OK)
        except Campaign.DoesNotExist:
            return Response({"error": "Campaigns not available"}, status=status.HTTP_404_NOT_FOUND)
