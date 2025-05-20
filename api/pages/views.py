import json
import uuid

from django.db.models import Q
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.generics import (
    RetrieveAPIView, ListAPIView,
)
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from wagtail.blocks import StreamValue
from wagtail.images.models import Image

from api.pages.serializers import FAQsSerializer, BusinessSerializer, AboutSerializer, PricingSerializer, \
    JoinTheWooSerializer, InfluencerSerializer, InfluencerListSerializer, RestaurantListSerializer, \
    RestaurantSerializer, UpdateInfluencerSerializer, RestaurantReviewSerializer, RestaurantRecommendationSerializer, \
    RestaurantDetailSerializer, RestaurantDetailsSerializer, RestaurantCreateSerializer
from api.serializers import Pagination, get_text, InfluPagination
from apps.main.helper import email_dict
from apps.main.models import FAQs, Business, About, Pricing, JoinTheWoo, Influencer, Restaurant, Review, Invitation, \
    RestaurantListing, Franchise
from apps.snippet.models import City, Category, Ambience
from send_email import send_email


class FAQsPageAPIViews(RetrieveAPIView):
    queryset = FAQs.objects.live()
    serializer_class = FAQsSerializer

    def get_object(self):
        return self.get_queryset().first()


class BusinessPageAPIView(RetrieveAPIView):
    queryset = Business.objects.live()
    serializer_class = BusinessSerializer

    def get_object(self):
        return self.get_queryset().first()


class AboutPageAPIView(RetrieveAPIView):
    queryset = About.objects.live()
    serializer_class = AboutSerializer

    def get_object(self):
        return self.get_queryset().first()


class JoinTheWooPageAPIView(RetrieveAPIView):
    queryset = JoinTheWoo.objects.live()
    serializer_class = JoinTheWooSerializer

    def get_object(self):
        return self.get_queryset().first()


class PricingPageAPIView(RetrieveAPIView):
    queryset = Pricing.objects.live()
    serializer_class = PricingSerializer

    def get_object(self):
        return self.get_queryset().first()


class InfluencerPageAPIView(APIView):
    queryset = Influencer.objects.live()
    serializer_class = InfluencerSerializer
    lookup_field = 'slug'

    def get(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug')
        if not slug:
            return Response({'error': 'Influencer does not exist'}, status=status.HTTP_404_NOT_FOUND)
        try:
            influencer = self.queryset.get(slug=slug)
            serializer = self.serializer_class(influencer).data
            return Response(serializer, status=status.HTTP_200_OK)
        except Restaurant.DoesNotExist:
            return Response({'error': 'Influencer does not exist'}, status=status.HTTP_404_NOT_FOUND)


class InfluencerListingPageAPIView(ListAPIView):
    queryset = Influencer.objects.live()
    serializer_class = InfluencerListSerializer
    pagination_class = None

    def get_queryset(self):
        city = self.request.query_params.get("city")
        state = self.request.query_params.get("state")
        city_wise = self.request.query_params.get("city-wise") == 'true'
        type = self.request.query_params.get("type")
        q = self.request.query_params.get("q")

        queryset = self.queryset.all()
        if city:
            queryset = queryset.filter(city__slug=city)
        elif city_wise:
            queryset = queryset.filter(city__slug=City.objects.first().slug)
        elif state:
            queryset = queryset.filter(city__state__slug=state)

        if type:
            queryset = queryset.filter(user__Restaurants__type=type)

        if q:
            queryset = queryset.filter(name__icontains=q)
        return queryset.distinct()

    def list(self, request, *args, **kwargs):
        is_paginate = self.request.query_params.get("is_pagination", 'false') == 'true'
        limit = self.request.query_params.get("limit")
        queryset = self.get_queryset().all()
        if is_paginate:
            paginator = InfluPagination()
            page = paginator.paginate_queryset(queryset, request, view=self)

            total_pages = (paginator.page.paginator.count // paginator.page_size) + (
                1 if paginator.page.paginator.count % paginator.page_size > 0 else 0)

            response_data = paginator.get_paginated_response(self.get_serializer(page, many=True).data).data
            response_data['total_pages'] = total_pages
            return Response(response_data, status=status.HTTP_200_OK)

        serializer = self.get_serializer(queryset, many=True)
        if limit:
            response_data = serializer.data[:int(limit)]
        else:
            response_data = serializer.data
        return Response(response_data, status=status.HTTP_200_OK)


class RestaurantListingPageAPIView(ListAPIView):
    queryset = Restaurant.objects.live()
    serializer_class = RestaurantListSerializer
    pagination_class = None

    def get_queryset(self):
        slug = self.request.query_params.get("slug")
        limit = self.request.query_params.get("limit")
        city = self.request.query_params.get("city")
        q = self.request.query_params.get("q")
        is_featured = self.request.query_params.get("is_featured")
        is_paginate = self.request.query_params.get("is_pagination", 'false') == 'true'
        is_influencer = self.request.query_params.get("is_influencer") == 'true'
        queryset = self.queryset.all()
        if not is_influencer:
            if slug:
                city_id = self.queryset.get(slug=slug).city.id
                queryset = self.queryset.filter(city_id=city_id).exclude(slug=slug)
            elif city:
                queryset = self.queryset.filter(city__slug=city)
            else:
                city = City.objects.first()
                queryset = self.queryset.filter(city__slug=city.slug)

        filters = {
            "city__state__slug": self.request.query_params.get("state"),
            "type": self.request.query_params.get("type"),
            "categories__id__in": self.request.query_params.getlist("categories") or self.request.query_params.getlist(
                "categories[]"),
            "budget_friendly__in": self.request.query_params.getlist(
                "budget-type") or self.request.query_params.getlist("budget-type[]"),
            "ambience__id__in": self.request.query_params.getlist("ambience") or self.request.query_params.getlist(
                "ambience[]"),
            "recommended_by__influencer__slug__in": self.request.query_params.getlist(
                "recommended-by") or self.request.query_params.getlist("recommended-by[]"),
        }
        filters = {k: v for k, v in filters.items() if v}

        q_objects = Q()
        for key, value in filters.items():
            q_objects &= Q(**{key: value})
        if q:
            q_objects = q_objects & (
                    Q(categories__name__icontains=q)
                    | Q(name__icontains=q)
                    | Q(slug__icontains=q)
                    | Q(recommended_by__influencer__name__icontains=q)
                    | Q(recommended_by__influencer__slug__icontains=q)
            )

        if is_featured:
            q_objects &= Q(is_featured=True)

        rating = self.request.query_params.getlist("rating") or self.request.query_params.getlist("rating[]")
        if rating:
            q_objects &= self.filter(rating)

        sort = self.request.query_params.get("sort")
        order_by = 'first_published_at' if sort == 'oldest' else '-first_published_at'
        queryset = queryset.filter(q_objects).distinct().order_by(order_by)

        if is_paginate:
            paginator = Pagination()
            page = paginator.paginate_queryset(queryset, self.request, view=self)

            response_data = paginator.get_paginated_response(page).data
            return response_data.get('results')

        if limit:
            queryset = queryset[:int(limit)]
        return queryset

    def filter(self, rating):
        filter_type = dict(heart='heart', diamond='diamond', thumb_up='thumb_up')
        q = Q()
        for r in rating:
            if r == filter_type['diamond']:
                q |= Q(rating__gt=4)
            elif r == filter_type['heart']:
                q |= Q(rating__range=(2.5, 4))
            elif r == filter_type['thumb_up']:
                q |= Q(rating__lt=2.5)
        return q


class RestaurantPageAPIView(APIView):
    queryset = Restaurant.objects.live()
    serializer_class = RestaurantSerializer
    lookup_field = 'slug'

    def get(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug')
        if not slug:
            return Response({'error': 'Restaurant does not exist'}, status=status.HTTP_404_NOT_FOUND)
        try:
            restaurant = self.queryset.get(slug=slug)
            serializer = self.serializer_class(restaurant).data
            return Response(serializer, status=status.HTTP_200_OK)
        except Restaurant.DoesNotExist:
            return Response({'error': 'Restaurant does not exist'}, status=status.HTTP_404_NOT_FOUND)


class UpdateInfluencerPageAPIView(APIView):
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser,)
    queryset = Influencer.objects.live()
    serializer_class = InfluencerSerializer

    def get(self, request, *args, **kwargs):
        try:
            queryset = self.queryset.get(user=request.user)
            serializer = UpdateInfluencerSerializer(queryset)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Influencer.DoesNotExist:
            return Response({"error": "Influencer not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, *args, **kwargs):
        queryset = self.queryset.get(user=request.user)
        serializer = UpdateInfluencerSerializer(queryset, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            print('saving')
            serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class RestaurantReviewsAPIView(APIView):
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = RestaurantReviewSerializer
    pagination_class = None
    queryset = Review.objects.all()

    def get(self, request, *args, **kwargs):
        restaurant_id = request.query_params.get("restaurant_id")
        limit = request.query_params.get("limit")
        sort = request.query_params.get("sort")
        q = request.query_params.get("q")
        is_paginate = request.query_params.get("is_pagination", 'false') == 'true'

        queryset = self.queryset.filter(restaurant_id=restaurant_id, is_published=True)
        extra_info = dict(no_of_reviews=queryset.count(), page_size=Pagination.page_size)

        if not queryset:
            return Response({"error": "No reviews Found"}, status=status.HTTP_404_NOT_FOUND)

        if q:
            query = Q(content__icontains=q) | Q(posted_by__first_name__icontains=q) | Q(
                posted_by__last_name__icontains=q) | Q(approved_by__name__icontains=q) | Q(
                posted_by__influencer__name__icontains=q)
            queryset = queryset.filter(query)

        if limit:
            queryset = queryset[:int(limit)]
        else:
            order_by = 'created_at' if sort == 'Oldest' else '-created_at'
            queryset = queryset.order_by(order_by)
        response_data = dict()
        if is_paginate:
            paginator = Pagination()
            page = paginator.paginate_queryset(queryset, request, view=self)

            serializer = self.serializer_class(page, many=True)
            response_data['data'] = paginator.get_paginated_response(serializer.data).data
        else:
            serializer = self.serializer_class(queryset, many=True)
            response_data['data'] = serializer.data
        response_data['pagination'] = extra_info
        return Response(response_data, status=status.HTTP_200_OK)


class RestaurantRecommendationAPIView(APIView):
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = RestaurantRecommendationSerializer
    pagination_class = None
    queryset = Restaurant.objects.all()

    def get(self, request, *args, **kwargs):
        restaurant_id = request.query_params.get("restaurant_id")
        limit = request.query_params.get("limit")
        sort = request.query_params.get("sort")

        q = request.query_params.get("q")

        try:
            queryset = self.queryset.get(id=restaurant_id)

            serializer = self.serializer_class(queryset)
            data = serializer.data

            if q:
                recommended_by = []
                for item in data.get('recommended_by'):
                    try:
                        if q.lower() in item.get('influencer', {}).get('name', '').lower():
                            recommended_by.append(item)
                    except:
                        if q.lower() in item.get('user', {}).get('name', '').lower():
                            recommended_by.append(item)
                data['recommended_by'] = recommended_by

            if sort == 'Oldest':
                data['recommended_by'] = data['recommended_by'][::-1]

            if limit:
                data = {'id': data.get('id'), 'recommended_by': data.get('recommended_by')[:int(limit)]}
            return Response(data, status=status.HTTP_200_OK)

        except Restaurant.DoesNotExist:
            return Response({"error": "No Recommendation Found"}, status=status.HTTP_404_NOT_FOUND)


class RestaurantDetailsAPIView(APIView):
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = RestaurantDetailSerializer
    queryset = Restaurant.objects.all()

    def get(self, request, *args, **kwargs):
        restaurant_id = request.query_params.get("restaurant_id")
        try:
            queryset = self.queryset.get(id=restaurant_id)
            serializer = self.serializer_class(queryset, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Restaurant.DoesNotExist:
            return Response({"error": "Restaurant not Found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, *args, **kwargs):
        restaurant_id = request.query_params.get("restaurant_id")
        try:
            queryset = self.queryset.get(id=restaurant_id)
            serializer = self.serializer_class(queryset, data=request.data, partial=True, context={'request': request})
            if serializer.is_valid(raise_exception=True):
                serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        except:
            return Response({"error": "Restaurant not Found"}, status=status.HTTP_404_NOT_FOUND)


class RestaurantDetailAPIView(APIView):
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = RestaurantDetailsSerializer
    queryset = Restaurant.objects.live()
    lookup_field = 'pk'

    def get(self, request, *args, **kwargs):
        restaurant_id = kwargs.get("pk")
        try:
            queryset = self.queryset.get(id=restaurant_id)
            serializer = self.serializer_class(queryset)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Restaurant.DoesNotExist:
            return Response({"error": "Restaurant not Found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, *args, **kwargs):

        if not request.data.get('data'):
            return Response({"error": "Provide restaurant data"}, status=status.HTTP_404_NOT_FOUND)
        try:
            queryset = self.queryset.get(id=kwargs.get("pk"))
            serializer = self.serializer_class(queryset, data=request.data, partial=True, context={'request': request})
            if serializer.is_valid(raise_exception=True):
                serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        except:
            return Response({"error": "Restaurant not Found"}, status=status.HTTP_404_NOT_FOUND)


class RestaurantCreateAPIView(APIView):
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = RestaurantCreateSerializer

    def post(self, request, *args, **kwargs):
        if not request.data.get('data'):
            return Response({"error": "Provide restaurant data"}, status=status.HTTP_404_NOT_FOUND)

        data = json.loads(request.data.get('data'))
        menus = request.data.getlist('menus[]')
        photos = request.data.getlist('photos[]')
        profile = request.data.get('profile[]')
        if data.get('franchise'):
            franchise = Franchise.objects.filter(id=data.get('franchise')).first()
        else:
            franchise = None
        if not profile:
            return Response({"error": "Provide profile picture"}, status=status.HTTP_404_NOT_FOUND)

        if not menus:
            return Response({"error": "Provide Menus picture"}, status=status.HTTP_404_NOT_FOUND)

        if not photos:
            return Response({"error": "Provide photos picture"}, status=status.HTTP_404_NOT_FOUND)
        id = uuid.uuid4()
        parent_page = RestaurantListing.objects.first()
        restaurant = parent_page.add_child(
            instance=Restaurant(title=id,
                                slug=id,
                                name=franchise.name if franchise else data.get('name') ,
                                short_description=data.get('short_description'),
                                about_restaurant=data.get('about_restaurant'),
                                email=data.get('email'),
                                phone_number=data.get('phone_number'),
                                location=data.get('map'),
                                type=data.get('type'),
                                reservation_time=data.get('reservation_time'),
                                budget_friendly=data.get('budget_friendly'),
                                )
        )
        if franchise:
            restaurant.franchise = franchise
            restaurant.is_franchise = True

        restaurant.categories.set(Category.objects.filter(id__in=data.get('categories', [])))
        restaurant.ambience.set(Ambience.objects.filter(id__in=data.get('ambience', [])))
        restaurant.city = City.objects.get(id=data.get('city', ''))
        restaurant.user = request.user

        if restaurant.restaurant_images is None:
            restaurant.restaurant_images = StreamValue(restaurant.restaurant_images.stream_block, [])

        if restaurant.menus is None:
            restaurant.menus = StreamValue(restaurant.menus.stream_block, [])

        images = list(restaurant.restaurant_images)
        for img_file in photos:
            wagtail_image = Image.objects.create(title=img_file.name, file=img_file)
            images.append(('image', wagtail_image))

        restaurant.restaurant_images = StreamValue(
            restaurant.restaurant_images.stream_block,
            images
        )

        if menus:
            images = list(restaurant.menus)  # Ensure it's a list
            for img_file in menus:
                wagtail_image = Image.objects.create(title=img_file.name, file=img_file)
                images.append(('menu', wagtail_image))  # Append in the correct format

            restaurant.menus = StreamValue(
                restaurant.menus.stream_block,
                images
            )
        if profile:
            wagtail_image = Image.objects.create(title=profile.name,
                                                 file=profile)
            restaurant.profile_pic = wagtail_image

        restaurant.save()
        restaurant.save_revision().publish()

        e = [restaurant.user.email]
        body = 'emails/welcome-for-rest.html'
        context = dict(name=get_text(restaurant.name), **email_dict)
        subject_context = dict(subject='Welcome to WooMeNow!')
        send_email(e, body, context, subject_context)

        return Response({"message": "Restaurant Created Successfully"}, status=status.HTTP_201_CREATED)


class RestaurantInviteAPIView(APIView):
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        res = Invitation.objects.filter(invite_to=request.user.email)
        if res:
            return Response({'message': 'success'}, status=status.HTTP_200_OK)
        return Response({'error': 'Fail'}, status=status.HTTP_404_NOT_FOUND)
