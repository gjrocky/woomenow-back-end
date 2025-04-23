import json

from rest_framework import serializers
from wagtail.blocks import StreamValue
from wagtail.images.models import Image

from api.helper import StreamFieldSerializer, city, OrderedStreamFieldSerializer
from api.serializers import StreamFieldBlockSerializer, get_text
from apps.main.models import (
    FAQs, Business, About, Pricing, JoinTheWoo, Influencer, Restaurant, Review,
)
from apps.snippet.models import Category, Ambience


class FAQsSerializer(serializers.ModelSerializer):
    faqs = StreamFieldBlockSerializer(source="faq")

    class Meta:
        model = FAQs
        fields = ["id", "title", "slug", "faqs"]


class BusinessSerializer(serializers.ModelSerializer):
    key_point = StreamFieldBlockSerializer()
    why_choose_us_cards = StreamFieldBlockSerializer()
    win_plan_cards = StreamFieldBlockSerializer()
    faq = StreamFieldBlockSerializer()
    choose_image = serializers.SerializerMethodField(source="choose_image")
    CTA_btn = serializers.SerializerMethodField(source="CTA_btn")
    price_button = serializers.SerializerMethodField(source="price_btn")
    CTA_btn_icon = serializers.SerializerMethodField(source="CTA_btn_icon")

    def get_CTA_btn(self, obj):
        return get_text(obj.CTA_btn)

    def get_price_button(self, obj):
        return get_text(obj.price_btn)

    def get_choose_image(self, obj):
        try:
            return obj.choose_image.file.url
        except:
            return None

    def get_CTA_btn_icon(self, obj):
        try:
            return obj.CTA_btn_icon.file.url
        except:
            return None

    class Meta:
        model = Business
        fields = [
            "id",
            "title",
            "slug",
            "CTA_btn",
            "heading",
            "description",
            "video_1",
            "video_2",
            "video_3",
            "choose_heading",
            "choose_description",
            "choose_image",
            "win_plan_heading",
            "win_plan_description",
            "win_plan_cards",
            "why_choose_us_cards",
            "price_heading",
            "price_description",
            "price_button",
            "CTA_btn_icon",
            "faq",
            "key_point",
        ]


class AboutSerializer(serializers.ModelSerializer):
    cards = StreamFieldBlockSerializer(source="vision_points")

    class Meta:
        model = About
        fields = [
            "id",
            "title",
            "slug",
            "description",
            "heading",
            "vision_title",
            "image",
            "cards",
        ]


class JoinTheWooSerializer(serializers.ModelSerializer):
    Points = StreamFieldBlockSerializer(source="community_points")

    class Meta:
        model = JoinTheWoo
        fields = [
            "id",
            "title",
            "slug",
            "heading",
            "description",
            "about_community",
            "sub_heading",
            "Points",
        ]


class PricingSerializer(serializers.ModelSerializer):
    pricing_cards = StreamFieldBlockSerializer(source="cards")

    class Meta:
        model = Pricing
        fields = [
            "id",
            "title",
            "slug",
            "heading",
            "description",
            'note',
            'CTA_btn',
            'pricing_cards'
        ]


class InfluencerSerializer(serializers.ModelSerializer):
    city = serializers.SerializerMethodField(source='city')
    profile_image = serializers.SerializerMethodField(source='profile')
    restaurant_images = StreamFieldSerializer()
    social_links = StreamFieldSerializer()

    def get_city(self, obj):
        return city(obj)

    def get_profile_image(self, obj):
        try:
            return obj.profile.file.url
        except:
            return None

    class Meta:
        model = Influencer

        fields = ['id', 'title', 'slug', 'name', 'description', 'city', 'profile_image', 'restaurant_images',
                  'social_links']


class InfluencerListSerializer(serializers.ModelSerializer):
    profile_image = serializers.SerializerMethodField(source='profile')
    social_links = StreamFieldSerializer()
    recommendations = serializers.SerializerMethodField()

    def get_recommendations(self, obj):
        return [{"id": res.id, "name": get_text(res.name), "image": res.restaurant_images[0].value.file.url,
                 'city': res.city.name, 'state': res.city.state.ISO_code, "slug": res.slug} for res in
                obj.user.Restaurants.all()[:6]]

    def get_profile_image(self, obj):
        try:
            return obj.profile.file.url
        except:
            return None

    class Meta:
        model = Influencer

        fields = ['id', 'title', 'slug', 'name', 'profile_image', 'social_links', 'recommendations']


class RestaurantListSerializer(serializers.ModelSerializer):
    city = serializers.SerializerMethodField(source='city')
    categories = serializers.SerializerMethodField(source='categories')
    recommended_by = serializers.SerializerMethodField(source='recommended_by')
    restaurant_image = serializers.SerializerMethodField(source='restaurant_images')
    description = serializers.SerializerMethodField(source='short_description')

    def get_city(self, obj):
        return city(obj)

    def get_description(self, obj):
        return get_text(obj.short_description)

    def get_categories(self, obj):
        categories = obj.categories.all().values('name', 'id')
        if not categories:
            return []
        return categories

    def get_recommended_by(self, obj):
        recommended_by = obj.recommended_by.all().order_by('-influencer')
        if not recommended_by:
            return []
        r_by = []
        for r in recommended_by:
            try:
                influencer = dict(id=r.influencer.id, name=r.influencer.name,
                                  image=r.influencer.profile.file.url)
            except:
                influencer = None

            r_obj = dict(
                influencer=influencer,
                user=dict(id=r.id, name=r.first_name),
            )
            r_by.append(r_obj)
        return r_by

    def get_restaurant_image(self, obj):
        if not obj.restaurant_images:
            return ''
        return obj.restaurant_images[0].value.file.url

    class Meta:
        model = Restaurant

        fields = ['id', 'title', 'slug', 'name', 'is_featured', 'is_home_featured', 'rating', 'recommended_by',
                  'categories', 'city', 'description', 'restaurant_image', 'type', 'budget_friendly']


class RestaurantSerializer(serializers.ModelSerializer):
    menus = StreamFieldBlockSerializer()
    restaurant_images = StreamFieldBlockSerializer()
    city = serializers.SerializerMethodField(source='city')
    recommended_by = serializers.SerializerMethodField(source='recommended_by')
    categories = serializers.SerializerMethodField(source='categories')
    ambience = serializers.SerializerMethodField(source='ambience')

    def get_city(self, obj):
        return city(obj)

    def get_recommended_by(self, obj):
        recommended_by = obj.recommended_by.all().order_by('-influencer')
        if not recommended_by:
            return []
        r_by = []
        for r in recommended_by:
            try:
                influencer = dict(id=r.influencer.id, name=r.influencer.name,
                                  image=r.influencer.profile.file.url, slug=r.influencer.slug)
            except:
                influencer = None
            r_obj = dict(
                influencer=influencer,
                user=dict(id=r.id, name=r.first_name),
            )
            r_by.append(r_obj)
        return r_by

    def get_categories(self, obj):
        categories = obj.categories.all().values('name', 'id')
        if not categories:
            return []
        return categories

    def get_ambience(self, obj):
        return obj.ambience.all().values('name', 'id')

    class Meta:
        model = Restaurant
        fields = ['id', 'title', 'name', 'slug', 'short_description', 'about_restaurant', 'email', 'phone_number',
                  'location', 'menus', 'type', 'is_featured', 'is_home_featured', 'rating', 'website_url',
                  'budget_friendly', 'city', 'profile_pic', 'recommended_by', 'restaurant_images', 'categories',
                  'ambience', 'reservation_time']


class UpdateInfluencerSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField(source='profile')
    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    restaurant_images = OrderedStreamFieldSerializer()

    def get_name(self, obj):
        return get_text(obj.name)

    def get_description(self, obj):
        return get_text(obj.description)

    def get_profile(self, obj):
        try:
            return obj.profile.file.url
        except:
            return None

    class Meta:
        model = Influencer
        fields = ['id', 'name', 'description', 'profile', 'restaurant_images']

    def update(self, instance, validated_data):
        profile_picture = self.initial_data.get('file[]', None)
        res_files = self.initial_data.getlist('res_files[]', None)
        delete_img = self.initial_data.get('delete_id', None)

        if instance.restaurant_images is None:
            instance.restaurant_images = StreamValue(instance.restaurant_images.stream_block, [])

        if delete_img:
            updated_images = [
                img for img in instance.restaurant_images if
                img.block_type == "image" and img.value.id != int(delete_img)
            ]
            instance.restaurant_images = StreamValue(
                instance.restaurant_images.stream_block,
                [("image", img.value) for img in updated_images]
            )
            instance.save(update_fields=['restaurant_images'])

        if profile_picture:
            wagtail_image = Image.objects.create(title=profile_picture.name, file=profile_picture)
            instance.profile = wagtail_image  # Fix wrong field reference

        # 🔹 **APPEND NEW IMAGES**
        if res_files:
            images = list(instance.restaurant_images)  # Ensure it's a list
            for img_file in res_files:
                wagtail_image = Image.objects.create(title=img_file.name, file=img_file)
                images.append(('image', wagtail_image))  # Append in the correct format

            instance.restaurant_images = StreamValue(
                instance.restaurant_images.stream_block,
                images
            )

        # 🔹 **UPDATE OTHER FIELDS**
        instance.name = self.initial_data.get('name', instance.name)
        instance.description = self.initial_data.get('description', instance.description)

        instance.save()
        return instance


class RestaurantReviewSerializer(serializers.ModelSerializer):
    posted_by = serializers.SerializerMethodField(source='posted_by')
    created_at = serializers.SerializerMethodField()
    approved_by = serializers.SerializerMethodField()

    def get_approved_by(self, obj):
        try:
            return dict(
                id=obj.approved_by.id,
                name=get_text(obj.approved_by.name),
                slug=obj.approved_by.slug,
            )
        except:
            return None

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
        except:
            try:
                profile = obj.posted_by.wagtail_userprofile.avatar.url
            except:
                profile = None

            return dict(
                id=obj.posted_by.id,
                name=f'{obj.posted_by.first_name} {obj.posted_by.last_name}',
                email=obj.posted_by.email,
                image=profile,
            )

    def get_created_at(self, obj):
        return obj.created_at.strftime("%b %d, %Y")

    class Meta:
        model = Review
        fields = ['id', 'content', 'rating', 'approved_by', 'posted_by',
                  'more_info', 'created_at']


class RestaurantRecommendationSerializer(serializers.ModelSerializer):
    recommended_by = serializers.SerializerMethodField(source='recommended_by')

    def get_recommended_by(self, obj):
        recommended_by = obj.recommended_by.all().order_by('-influencer')
        if not recommended_by:
            return []
        r_by = []
        for r in recommended_by:
            try:
                influencer = dict(id=r.influencer.id, name=get_text(r.influencer.name),
                                  image=r.influencer.profile.file.url)
            except:
                influencer = None
            r_obj = dict(
                influencer=influencer,
                user=dict(id=r.id, name=get_text(r.first_name), email=r.email),
            )
            r_by.append(r_obj)
        return r_by

    class Meta:
        model = Restaurant
        fields = ['id', 'recommended_by']


class RestaurantDetailSerializer(serializers.ModelSerializer):
    menus = serializers.SerializerMethodField()
    restaurant_images = OrderedStreamFieldSerializer()

    def get_menus(self, obj):
        if not obj.menus:
            return []

        return list(reversed([
            dict(id=img.value.id, type='image', url=img.value.file.url)
            for img in obj.menus
        ]))

    class Meta:
        model = Restaurant
        fields = ['id', 'restaurant_images', 'menus']

    def to_representation(self, instance):
        data = super().to_representation(instance)

        request = self.context.get('request', None)
        if request:
            if "/restaurant-menus/" in request.path:  # Only include `menus` in menu API
                data.pop('restaurant_images', None)
            elif "/restaurant-images/" in request.path:  # Only include `restaurant_images` in restaurant images API
                data.pop('menus', None)

        return data

    def update(self, instance, validated_data):
        res_files = self.initial_data.getlist('res_files[]', None)
        res_menu = self.initial_data.getlist('res_menu[]', None)
        delete_img = self.initial_data.get('delete_id', None)
        delete_menu = self.initial_data.get('delete_menu', None)

        if instance.restaurant_images is None:
            instance.restaurant_images = StreamValue(instance.restaurant_images.stream_block, [])

        if instance.menus is None:
            instance.menus = StreamValue(instance.menus.stream_block, [])

        if delete_img:
            updated_images = [
                img for img in instance.restaurant_images if
                img.block_type == "image" and img.value.id != int(delete_img)
            ]
            instance.restaurant_images = StreamValue(
                instance.restaurant_images.stream_block,
                [("image", img.value) for img in updated_images]
            )
            instance.save(update_fields=['restaurant_images'])

        if delete_menu:
            updated_images = [
                img for img in instance.menus if
                img.block_type == "menu" and img.value.id != int(delete_menu)
            ]
            instance.menus = StreamValue(
                instance.menus.stream_block,
                [("menu", img.value) for img in updated_images]
            )
            instance.save(update_fields=['menus'])

        if res_files:
            images = list(instance.restaurant_images)  # Ensure it's a list
            for img_file in res_files:
                wagtail_image = Image.objects.create(title=img_file.name, file=img_file)
                images.append(('image', wagtail_image))  # Append in the correct format

            instance.restaurant_images = StreamValue(
                instance.restaurant_images.stream_block,
                images
            )
        if res_menu:
            images = list(instance.menus)  # Ensure it's a list
            for img_file in res_menu:
                wagtail_image = Image.objects.create(title=img_file.name, file=img_file)
                images.append(('menu', wagtail_image))  # Append in the correct format

            instance.menus = StreamValue(
                instance.menus.stream_block,
                images
            )
        instance.save()
        return instance


class RestaurantDetailsSerializer(serializers.ModelSerializer):
    ambience = serializers.SerializerMethodField(source='ambience')
    categories = serializers.SerializerMethodField(source='categories')
    name = serializers.SerializerMethodField()
    short_description = serializers.SerializerMethodField()
    about_restaurant = serializers.SerializerMethodField()
    profile_pic = serializers.SerializerMethodField()

    def get_profile_pic(self, obj):
        try:
            return obj.profile_pic.file.url
        except:
            return None

    def get_name(self, obj):
        return get_text(obj.name)

    def get_short_description(self, obj):
        return get_text(obj.short_description)

    def get_about_restaurant(self, obj):
        return get_text(obj.about_restaurant)

    def get_categories(self, obj):
        categories = obj.categories.all()
        if categories:
            return [dict(id=cat.id, name=cat.name, slug=cat.slug) for cat in categories]
        return []

    def get_ambience(self, obj):
        ambience = obj.ambience.all()
        if ambience:
            return [dict(id=amb.id, name=amb.name) for amb in ambience]
        return []

    class Meta:
        model = Restaurant
        fields = ['id', 'slug', 'title', 'name', 'short_description', 'about_restaurant', 'email', 'phone_number',
                  'reservation_time', 'budget_friendly', 'categories', 'ambience', 'profile_pic', 'type']

    def update(self, instance, validated_data):
        data = json.loads(self.initial_data.get('data'))
        instance.name = data.get('name', instance.name)
        instance.short_description = data.get('short_description', instance.short_description)
        instance.about_restaurant = data.get('about_restaurant', instance.about_restaurant)
        instance.email = data.get('email', instance.email)
        instance.phone_number = data.get('phone_number', instance.phone_number)
        instance.budget_friendly = data.get('budget_friendly', instance.budget_friendly)
        instance.categories.set(Category.objects.filter(id__in=data.get('categories')))
        instance.ambience.set(Ambience.objects.filter(id__in=data.get('ambience')))
        if data.get('reservation_time'):
            instance.reservation_time = dict(reservation=data.get('reservation_time'))

        if self.initial_data.get('files[]'):
            wagtail_image = Image.objects.create(title=self.initial_data.get('files[]').name,
                                                 file=self.initial_data.get('files[]'))
            instance.profile_pic = wagtail_image

        instance.save()
        return instance


class RestaurantCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = '__all__'
