from django.db.models import Q
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListCreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from api.constants import QUERY_PARAMS
from api.forms.serializers import IPLocationSerializer, ContactSerializer, InvitationSerializer, ReviewSerializer, \
    JoinTheWooSerializer
from apps.main.models import Invitation, Review, Restaurant
from apps.snippet.models import IPLocation, Contact, JoinTheWooForm
from apps.users.models import User


class IPLocationAPIView(CreateAPIView):
    queryset = IPLocation.objects.all()
    serializer_class = IPLocationSerializer

    def perform_create(self, serializer):
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)


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


# @extend_schema(
#     parameters=[
#         OpenApiParameter(
#             name="user", description="User ID", required=False, type=int
#         ),
#         OpenApiParameter(
#             name="restaurant", description="Restaurant ID", required=False, type=int
#         )
#     ]
# )
# class ReviewAPIView(ListCreateAPIView):
#     queryset = Review.objects.all()
#     serializer_class = ReviewSerializer
#
#     def get_queryset(self):
#         queryset = super(ReviewAPIView, self).get_queryset()
#         filter_query = Q()
#         query_params = dict(
#             posted_by_id=self.request.query_params.get(QUERY_PARAMS["user"]),
#             restaurant_id=self.request.query_params.get(
#                 QUERY_PARAMS["restaurant"]
#             ),
#         )
#         for key, value in query_params.items():
#             if value:
#                 filter_query &= Q(**{key: value})
#
#         queryset = queryset.filter(filter_query)
#         return queryset
#
#     def perform_create(self, serializer):
#         if serializer.is_valid(raise_exception=True):
#             return Response(
#                 {"message": "Form submitted successfully"}, status=status.HTTP_200_OK
#             )
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ReviewAPIView(APIView):
    def get(self, request, *args, **kwargs):
        reviews = Review.objects.all()
        filter_query = Q()
        query_params = dict(
            posted_by_id=self.request.query_params.get(QUERY_PARAMS["user"]),
            restaurant_id=self.request.query_params.get(
                QUERY_PARAMS["restaurant"]
            ),
        )
        for key, value in query_params.items():
            if value:
                filter_query &= Q(**{key: value})

        reviews = reviews.filter(filter_query)

        if reviews:
            serializer = ReviewSerializer(reviews, many=True)
            return Response(serializer.data)
        else:
            return Response({"error": "reviews not found"}, status=404)

    def post(self, request, *args, **kwargs):
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = User.objects.get(id=request.data["posted_by_id"])
                restaurant = Restaurant.objects.get(id=request.data["restaurant_id"])
            except Exception as e:
                return Response(e, status=status.HTTP_400_BAD_REQUEST)
            instance = serializer.save()
            instance.posted_by = user
            instance.restaurant = restaurant
            instance.save()
            return Response(ReviewSerializer(instance).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
