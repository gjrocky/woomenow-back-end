from django.contrib.auth.hashers import check_password
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, SerializerMethodField

from api.helper import password_checker
from api.serializers import get_text
from apps.users.models import User


class UserSerializer(ModelSerializer):
    restaurants = SerializerMethodField()
    city = SerializerMethodField()
    is_influencer = SerializerMethodField()

    def get_city(self, obj):
        if obj.city:
            return dict(name=obj.city.name, state=dict(name=obj.city.state.name, ISO_code=obj.city.state.ISO_code))
        return None

    def get_is_influencer(self, obj):
        try:
            if obj.influencer:
                return True
            return False
        except:
            return False

    def get_restaurants(self, obj):
        restaurants = obj.restaurants.all()
        if not restaurants:
            return []
        data = []
        for res in restaurants:
            try:
                img = res.profile_pic.file.url
            except:
                img = None
            data.append({'id': res.id,
                         'name': get_text(res.name),
                         'image': img,
                         'city': dict(name=obj.city.name,
                                      state=dict(
                                          name=obj.city.state.name,
                                          ISO_code=obj.city.state.ISO_code))
                         }
                        )
        return data

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'profile_picture', 'point', 'restaurants', 'city',
                  'is_influencer', 'phone', 'date_of_birth']

    def update(self, instance, validated_data):
        profile_picture = self.initial_data.get('file[]', None)
        if profile_picture:
            instance.profile_picture = profile_picture
        instance.first_name = self.initial_data.get('first_name', instance.first_name)
        instance.last_name = self.initial_data.get('last_name', instance.last_name)
        instance.phone = self.initial_data.get('phone', instance.phone)
        if self.initial_data.get("date_of_birth"):
            date_str = self.initial_data.get("date_of_birth", instance.date_of_birth)
            if date_str and isinstance(date_str, str):
                date_str = date_str.split("T")[0]

            instance.date_of_birth = date_str
        instance.point = validated_data.get('point', instance.point)

        old_password = self.initial_data.get('password', None)
        new_password = self.initial_data.get('newPassword', None)
        confirm_password = self.initial_data.get('confirmNewPassword', None)

        if old_password and new_password and confirm_password:
            if not check_password(old_password, instance.password):
                raise serializers.ValidationError({"old_password": "Old password is incorrect."})

            if new_password != confirm_password:
                raise serializers.ValidationError({"confirm_password": "New passwords do not match."})

            password, is_not_valid_pass = password_checker(new_password)

            if is_not_valid_pass:
                raise serializers.ValidationError({"error": password})

            instance.set_password(new_password)

        instance.save()
        return instance
