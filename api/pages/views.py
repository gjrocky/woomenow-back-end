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

from api.pages.serializers import FAQsSerializer, BusinessSerializer, AboutSerializer, PricingSerializer, \
    JoinTheWooSerializer, InfluencerSerializer, InfluencerListSerializer, RestaurantListSerializer, \
    RestaurantSerializer, UpdateInfluencerSerializer, RestaurantReviewSerializer, RestaurantRecommendationSerializer, \
    RestaurantDetailSerializer
from api.serializers import Pagination
from apps.main.models import FAQs, Business, About, Pricing, JoinTheWoo, Influencer, Restaurant, Review
from apps.snippet.models import City


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


class InfluencerPageAPIView(RetrieveAPIView):
    queryset = Influencer.objects.live()
    serializer_class = InfluencerSerializer
    lookup_field = 'pk'


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
        return queryset

    def list(self, request, *args, **kwargs):
        is_paginate = self.request.query_params.get("is_pagination", 'false') == 'true'
        limit = self.request.query_params.get("limit")
        queryset = self.get_queryset().all()
        if is_paginate:
            paginator = Pagination()
            page = paginator.paginate_queryset(queryset, request, view=self)

            total_pages = (paginator.page.paginator.count // paginator.page_size) + (
                1 if paginator.page.paginator.count % paginator.page_size > 0 else 0)

            response_data = paginator.get_paginated_response(self.get_serializer(page, many=True).data).data
            response_data['total_pages'] = total_pages
            return Response(response_data)

        serializer = self.get_serializer(queryset, many=True)
        if limit:
            response_data = serializer.data[:int(limit)]
        else:
            response_data = serializer.data
        return Response(response_data)


class RestaurantListingPageAPIView(ListAPIView):
    queryset = Restaurant.objects.live()
    serializer_class = RestaurantListSerializer
    pagination_class = None

    def get_queryset(self):
        id = self.request.query_params.get("id")
        limit = self.request.query_params.get("limit")
        city = self.request.query_params.get("city")
        q = self.request.query_params.get("q")
        is_featured = self.request.query_params.get("is_featured")
        if id:
            city_id = self.queryset.get(id=id).city.id
            queryset = self.queryset.filter(city_id=city_id).exclude(id=id)
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
                "budget-type") or self.request.query_params.getlist(
                "budget-type[]"),
            "ambience__id__in": self.request.query_params.getlist("ambience") or self.request.query_params.getlist(
                "ambience[]"),
            "recommended_by__influencer__id__in": self.request.query_params.getlist(
                "recommended-by") or self.request.query_params.getlist(
                "recommended-by[]"),
        }
        filters = {k: v for k, v in filters.items() if v}

        q_objects = Q()
        for key, value in filters.items():
            q_objects &= Q(**{key: value})
        if q:
            q_objects = q_objects & (
                    Q(categories__name__icontains=q) | Q(name__icontains=q) | Q(
                recommended_by__influencer__name__icontains=q))
        if is_featured:
            q_objects &= Q(is_featured=True)

        rating = self.request.query_params.getlist("rating") or self.request.query_params.getlist("rating[]")
        if rating:
            q_objects &= self.filter(rating)

        sort = self.request.query_params.get("sort")
        order_by = 'first_published_at' if sort == 'oldest' else '-first_published_at'
        queryset = queryset.filter(q_objects).distinct().order_by(order_by)

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


class RestaurantPageAPIView(RetrieveAPIView):
    queryset = Restaurant.objects.live()
    serializer_class = RestaurantSerializer
    lookup_field = 'pk'


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
            return Response({"message": "Influencer not found"}, status=status.HTTP_404_NOT_FOUND)

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
        queryset = self.queryset.filter(restaurant_id=restaurant_id, is_published=True)
        if not queryset:
            return Response({"message": "No reviews Found"}, status=status.HTTP_404_NOT_FOUND)

        if limit:
            queryset = queryset[:int(limit)]

        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RestaurantRecommendationAPIView(APIView):
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = RestaurantRecommendationSerializer
    pagination_class = None
    queryset = Restaurant.objects.all()

    def get(self, request, *args, **kwargs):
        restaurant_id = request.query_params.get("restaurant_id")
        limit = request.query_params.get("limit")
        try:
            queryset = self.queryset.get(id=restaurant_id)

            serializer = self.serializer_class(queryset)
            data = serializer.data
            if limit:
                data = {'id': data.get('id'), 'recommended_by': data.get('recommended_by')[:int(limit)]}
            return Response(data, status=status.HTTP_200_OK)

        except Restaurant.DoesNotExist:
            return Response({"message": "No Recommendation Found"}, status=status.HTTP_404_NOT_FOUND)


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
            return Response({"message": "Restaurant not Found"}, status=status.HTTP_404_NOT_FOUND)
