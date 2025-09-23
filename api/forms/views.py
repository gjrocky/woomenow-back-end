import logging
import uuid
from datetime import timedelta

import requests
from bs4 import BeautifulSoup
from django.conf import settings
from django.db.models import Q
from django.http.request import QueryDict
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.timezone import now, localtime
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
    JoinTheWooSerializer, GiveOfferSerializer
from api.serializers import Pagination
from api.serializers import ReviewSerializer as RSerializer
from apps.main.helper import email_dict
from apps.main.models import Invitation, Review, Restaurant, BecomeInfluencer, Influencer, EmailExecution
from apps.main.tasks import send_negative_reviews_email_step, send_restaurant_email_step
from apps.snippet.models import IPLocation, Contact, JoinTheWooForm, City, Campaign, CampaignTracker, EmailTemplate, \
    EmailTemplateChoice, EmailCategory
from send_custom_email import send_db_email
from send_email import send_email

logger = logging.getLogger(__name__)

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
        category = get_object_or_404(EmailCategory, slug='general-flow')
        template_choice = get_object_or_404(EmailTemplateChoice, category=category, choice_id=1)
        email_template = EmailTemplate.objects.filter(template=template_choice).first()
        if not email_template:
            return Response(
                {"error": f"No email template found for choice {template_choice.label}"},
                status=status.HTTP_404_NOT_FOUND,
            )
        context_data = {
            "name": serializer.initial_data.get('name'),
            "email": serializer.initial_data.get('email'),
            "phone": serializer.initial_data.get('phone'),
            "category": serializer.initial_data.get('category'),
            "message": serializer.initial_data.get('message'),
            **email_dict,
        }
        email = [settings.EMAIL_WOO_ME_NOW_CONTACT_EMAIL]
        # body = 'emails/contact-us.html'
        # subject_context = dict(subject=f'Contact Query - {serializer.initial_data.get("subject")}')
        # send_email(email, body, context, subject_context)
        send_db_email(email, template_choice, context_data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class JoinTheWooAPIView(CreateAPIView):
    queryset = JoinTheWooForm.objects.all()
    serializer_class = JoinTheWooSerializer

    def perform_create(self, serializer):
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        email = [settings.EMAIL_WOO_ME_NOW_CONTACT_EMAIL]
        body = 'emails/jointhewoo.html'
        context = dict(
            name=serializer.initial_data.get('name'),
            email=serializer.initial_data.get('email'),
            phone=serializer.initial_data.get('phone'),
            city=serializer.initial_data.get('city'),
            **email_dict
        )
        subject_context = dict(subject="New Join the Woo Submission")
        send_email(email, body, context, subject_context)
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

        # Extract question-ratings as dictionary
        describe_restaurant_ratings = {}
        question_ratings = []
        i = 0
        while True:
            question_key = f'describe_restaurant_ratings[{i}][question]'
            rating_key = f'describe_restaurant_ratings[{i}][rating]'
            if question_key in data and rating_key in data:
                question = data.get(question_key)
                try:
                    rating = int(data.get(rating_key))
                except (TypeError, ValueError):
                    rating = 0
                describe_restaurant_ratings[question] = rating
                if rating > 0:
                    question_ratings.append(rating)
                i += 1
            else:
                break

        # New average rating based on Q1–Q5 only
        if question_ratings:
            total_rating = round(sum(question_ratings) / len(question_ratings), 2)
        else:
            total_rating = 0

        if not request.data.get('res_id'):
            return Response({'error': 'Provide the restaurant ID'}, status=status.HTTP_400_BAD_REQUEST)

        # more_info JSON
        json_data = dict(
            describe_restaurant_ratings=describe_restaurant_ratings,
        )

        # Create review object
        review = Review(
            posted_by=request.user,
            content=data.get('message'),
            rating=total_rating,
            restaurant_id=data.get('res_id'),
            more_info=json_data,
            created_at=now(),
        )

        # Attach bill image (optional)
        if bill:
            wagtail_image = Image.objects.create(title=bill.name, file=bill)
            review.bill = wagtail_image

        review.save()

        try:
            res = Restaurant.objects.get(id=request.data.get('res_id'))
            # threading.Thread(target=self.send_influencer_emails, args=(review, res, email_dict)).start()
            if review.rating < 4:
                category = get_object_or_404(EmailCategory, slug='negative-review-flow')
                template_choice = get_object_or_404(EmailTemplateChoice, category=category, choice_id=1)
                email_template = EmailTemplate.objects.filter(template=template_choice).first()

                if email_template:
                    restaurant_email = [res.email]
                    name = strip_tags(res.name)

                    # Calculate automation_end_time (final step 5 execution time)
                    countdown_per_step = 24*60*60  # 60 seconds per step for production 24*60*60 24hrs
                    total_steps = 5
                    automation_end_time = timezone.localtime(
                        timezone.now() + timedelta(seconds=(total_steps - 1) * countdown_per_step)
                    )

                    context_data = {
                        "business_name": name,
                        "restaurant": res.id,
                        **email_dict,
                    }

                    execution_id = str(uuid.uuid4())

                    send_db_email(restaurant_email, template_choice, context_data, execution_id)
                    logger.info(f"[Review] Step 1 email sent to {restaurant_email} "
                                f"(choice id: {template_choice.choice_id}) for execution_id={execution_id} "
                                f"at {timezone.localtime(timezone.now()).strftime('%d %b %Y %I:%M %p')}")

                    execution = EmailExecution.objects.create(
                        execution_id=execution_id,
                        recipient_email=restaurant_email[0],
                        recipient_name=name,
                        current_step=1,
                        execution_flow=category.slug,
                        last_sent_at=timezone.now(),
                        last_sent_template_id=template_choice.choice_id,
                        is_active=True,
                    )
                    logger.info(f"[Review] Created EmailExecution {execution.execution_id} "
                                f"for {restaurant_email[0]} in flow {category.slug}")

                    # Schedule Step 2
                    countdown_seconds = 24*60*60  # for production 24*60*60 24hrs
                    send_negative_reviews_email_step.apply_async(
                        args=[str(execution.execution_id), 2, res.id, automation_end_time.isoformat()],
                        countdown=countdown_seconds)
                    logger.info(f"[Review] Scheduled step 2 for execution_id={execution.execution_id} "
                                f"in {countdown_seconds}s")

            return Response(
                {'message': 'Your review has been published after verification.'},
                status=status.HTTP_201_CREATED
            )

        except Restaurant.DoesNotExist:
            return Response(
                {'error': 'Provided Restaurant ID does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )


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
        # Old influencer GET logic commented out
        # try:
        #     influ = user.influencer
        #     queryset = Invitation.objects.filter(invited_by=influ)
        #     serializer = InvitationSerializer(queryset, many=True)
        #     return Response(serializer.data, status=status.HTTP_200_OK)
        # except Exception as e:

        if user.is_superuser:
            queryset = Invitation.objects.filter(super_user=user)
            serializer = InvitationSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(
            {'error': 'You are not authorized to view this data'},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    def post(self, request, *args, **kwargs):
        user = request.user

        invite_type = request.data.get('type')
        recommend_by = request.data.get("recommend_by", {})
        influencer_name = recommend_by.get("label") if recommend_by else None

        type_to_choice_id = {
            "dining": 1,
            "experience": 2,
        }
        choice_id = type_to_choice_id.get(invite_type)

        if not choice_id:
            return Response(
                {"error": f"Invalid type '{invite_type}'. Must be dining/restaurant/experience."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        category = get_object_or_404(EmailCategory, slug="restaurant-and-experience-onboarding-playbook")
        template_choice = get_object_or_404(
            EmailTemplateChoice,
            category=category,
            choice_id=choice_id
        )

        email_template = EmailTemplate.objects.filter(template=template_choice).first()
        if not email_template:
            return Response(
                {"error": f"No email template found for choice {template_choice.label}"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = InvitationSerializer(data={**request.data, "user": user})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # send email
        restaurant_email = [request.data.get("invite_to")]
        restaurant_name = request.data.get("restaurant_name")
        context_data = {
            "username": restaurant_name,
            "influencer_name": influencer_name,
            **email_dict,
        }
        execution_id = str(uuid.uuid4())

        try:
            send_db_email(restaurant_email, template_choice, context_data, execution_id)
            logger.info(
                f"[API] Manual email sent: '{template_choice.label}' "
                f"(ID: {template_choice.choice_id}) to {restaurant_email}"
            )
        except Exception as e:
            logger.error(f"[API] Failed to send manual email: {e}")
            return Response({"error": f"Failed to send email: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        execution = EmailExecution.objects.create(
            execution_id=execution_id,
            recipient_email=restaurant_email[0],
            recipient_name=restaurant_name,
            current_step=1,
            last_sent_at=timezone.now(),
            last_sent_template_id=template_choice.choice_id,
            execution_flow=category.slug,
        )
        logger.info(f"[API] Created EmailExecution {execution.execution_id} for {restaurant_email[0]}")

        countdown_seconds = 24*60*60  # for production use 24*60*60.
        send_restaurant_email_step.apply_async(args=[execution_id, 2], countdown=countdown_seconds)
        logger.info(f"[API] Step 2 scheduled for execution_id={execution.execution_id} in {countdown_seconds}s")

        return Response(
            {"message": "Our team will check & verify the restaurant/experience"},
            status=status.HTTP_201_CREATED,
        )


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


class GiveOfferAPIView(APIView):
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = GiveOfferSerializer(data=request.data)
        if serializer.is_valid():
            give_offer = serializer.save()

            execution_id = request.data.get('execution_id')
            is_opened = request.data.get('is_opened')

            # check if is_opened is true in payload
            if is_opened and execution_id:
                execution = EmailExecution.objects.filter(
                    execution_id=execution_id, is_active=True
                ).first()
                if execution:
                    execution.is_opened = True
                    execution.is_active = False
                    execution.save()

                    try:
                        template_choice = EmailTemplateChoice.objects.filter(
                            category__slug="negative-review-flow",
                            choice_id=4
                        ).first()
                        if template_choice:
                            restaurant = Restaurant.objects.filter(
                                email=execution.recipient_email
                            ).first()

                            if restaurant:
                                context_data = {
                                    "business_name": execution.recipient_name,
                                    **email_dict,
                                }
                                send_db_email(
                                    [restaurant.email],
                                    template_choice,
                                    context_data,
                                    execution.execution_id,
                                )
                                logger.info(
                                    f"[GiveOffer] 4a email sent to {restaurant.email} "
                                    f"for execution_id={execution.execution_id}"
                                )
                    except Exception as e:
                        logger.error(f"[GiveOffer] Failed to send 4a email: {e}")

            try:
                if give_offer.review and give_offer.review.restaurant:
                    review = give_offer.review
                    restaurant = give_offer.review.restaurant
                    reviewer_name = f"{review.posted_by.first_name} {review.posted_by.last_name}"

                    offer_details = give_offer.get_goodwill_offer_display() or ""

                    if give_offer.goodwill_offer == "custom_offer" and give_offer.custom_offer:
                        offer_details = f"{offer_details}: {give_offer.custom_offer}"

                    context_data = {
                        "business_name": strip_tags(restaurant.name),  # restaurant name
                        "review_id": review.id,  # review id
                        "reviewer_name": reviewer_name,  # reviewer name
                        "rating": f"{review.rating:.1f}",  # review rating
                        "review_date": localtime(review.created_at).strftime(
                            "%Y-%m-%d"
                        ),  # review date
                        "message": give_offer.message,
                        "offer_details": offer_details,
                        **email_dict
                    }
                    template_choice = EmailTemplateChoice.objects.filter(
                        category__slug="general-flow",
                        choice_id=2
                    ).first()

                    if template_choice:
                        send_db_email(
                            [settings.EMAIL_WOO_ME_NOW_REVIEW_EMAIL],
                            template_choice,
                            context_data,
                            execution_id=None,
                            from_email=settings.EMAIL_WOO_ME_NOW_NO_REPLY_EMAIL,
                        )
                        logger.info(
                            f"[GiveOffer] Review email sent for review_id={review.id} "
                            f"to {settings.EMAIL_WOO_ME_NOW_REVIEW_EMAIL}"
                        )
            except Exception as e:
                logger.error(f"[GiveOffer] Failed to send review email: {e}")

            return Response(
                {
                    "message": "Offer Created Successfully",
                    "offer": GiveOfferSerializer(give_offer).data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
