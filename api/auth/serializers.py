from rest_framework.serializers import ModelSerializer

from apps.users.models import User


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'profile_picture', 'point']

    def update(self, instance, validated_data):
        profile_picture = validated_data.get('profile_picture', None)
        if profile_picture:
            instance.profile_picture = profile_picture
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.point = validated_data.get('point', instance.point)
        instance.save()

        return instance
