from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from api.forms.serializers import IPLocationSerializer, ContactSerializer
from apps.snippet.models import IPLocation, Contact


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
        pass
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
