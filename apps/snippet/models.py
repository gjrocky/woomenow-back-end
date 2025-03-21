import urllib.parse

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import OneToOneField, TextField
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel
from wagtail.search import index

CustomUser = get_user_model()


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class IPLocation(BaseModel):
    ip_address = models.GenericIPAddressField(unique=True, db_index=True)
    city = models.CharField(_("City"), max_length=100)
    state = models.CharField(_("State"), max_length=100)
    country = models.CharField(_("Country"), max_length=100)
    ISO = models.CharField(_("ISO Code"), max_length=100)
    extra = models.JSONField(_("Extra"), null=True, blank=True)

    def __str__(self):
        return self.ip_address

    class Meta:
        verbose_name = "IP Location"
        verbose_name_plural = "IP Location"


class State(BaseModel, index.Indexed):
    name = models.TextField(_("Name"), max_length=50)
    slug = models.TextField(_("Slug"), max_length=100, unique=True)
    ISO_code = models.TextField(_("ISO Code"), max_length=2, unique=True)

    panels = [
        FieldPanel("name"),
        FieldPanel("ISO_code"),
    ]

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    search_fields = [
        index.AutocompleteField("name"),
    ]

    class Meta:
        verbose_name = "State"
        verbose_name_plural = "States"


class City(BaseModel):
    name = models.TextField(_("Name"), max_length=50)
    slug = models.TextField(_("Slug"), max_length=100, unique=True)
    state = models.ForeignKey("State", on_delete=models.CASCADE, related_name="cities")

    panels = [
        FieldPanel("name"),
        FieldPanel("state"),
    ]

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "City"
        verbose_name_plural = "Cities"


class Locality(BaseModel):
    name = models.TextField(_("Name"), max_length=100)
    slug = models.TextField(_("Slug"), max_length=100, unique=True)
    city = models.ForeignKey(
        "City", on_delete=models.CASCADE, related_name="Localities"
    )

    panels = [
        FieldPanel("name"),
        FieldPanel("city"),
    ]

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Locality"
        verbose_name_plural = "Localities"


class Category(BaseModel):
    name = models.TextField(_("Name"), max_length=50)
    image = models.ForeignKey(
        "wagtailimages.Image",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="+")
    slug = models.TextField(_("Slug"), max_length=100, unique=True)

    panels = [
        FieldPanel("name"),
        FieldPanel("image"),
    ]

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"


class CampaignTracker(BaseModel):
    ip = models.CharField(_("IP Address"), max_length=30)
    location = models.CharField(_("Location"), max_length=255)
    user_device = models.TextField(_("User Device Details"), max_length=2000)
    extra_data = models.JSONField(_("extra"), null=True, blank=True)
    campaign = models.ForeignKey(
        "Campaign",
        null=True,
        on_delete=models.SET_NULL,
        related_name="campaign_tracker",
    )

    panels = [
        FieldPanel("ip", read_only=True),
        FieldPanel("location", read_only=True),
        FieldPanel("user_device", read_only=True),
        FieldPanel("campaign", read_only=True),
        FieldPanel("extra_data", read_only=True),
    ]

    def __str__(self):
        return self.ip

    class Meta:
        verbose_name = "Campaign Tracker"
        verbose_name_plural = "Campaign Tracker"


class Campaign(BaseModel):
    name = models.CharField(_("Campaign Name"), max_length=200)
    utm_source = models.CharField(_("UTM Source"), max_length=50)
    utm_medium = models.CharField(_("UTM Medium"), max_length=50)
    utm_campaign = models.CharField(_("UTM Campaign"), max_length=50)
    redirect_to = models.CharField(_("Redirect To"), max_length=50)
    is_active = models.BooleanField(_("Is Active"), default=False)
    slug = models.CharField(_("Slug"), max_length=50, unique=True, db_index=True)

    def __str__(self):
        return f"{self.name} - {str(self.redirect_to)}"

    class Meta:
        verbose_name = "Campaign"
        verbose_name_plural = "Campaigns"

    @property
    def get_query_string(self):
        return urllib.parse.urlencode(
            dict(
                utm_source=slugify(self.utm_source),
                utm_medium=slugify(self.utm_medium),
                utm_campaign=slugify(self.utm_campaign),
            )
        )


class Contact(BaseModel):
    name = models.CharField(_("Name"), max_length=50)
    email = models.EmailField(_("Email"))
    phone = models.CharField(_("Phone"), max_length=20, null=True, blank=True)
    subject = models.CharField(_("Subject"), max_length=100)
    message = models.TextField(_("Message"), max_length=5000)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Contact"
        verbose_name_plural = "Contacts"


class JoinTheWooForm(BaseModel):
    name = models.CharField(_("Name"), max_length=50)
    email = models.EmailField(_("Email"))
    phone = models.CharField(_("Phone"), max_length=20, null=True, blank=True)
    city = models.CharField(_("City"), max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Join The Woo"
        verbose_name_plural = "Join The Woo"


class Point(BaseModel):
    user = OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="points")
    content = TextField(_("Content"), max_length=5000)

    def __str__(self):
        return self.user.first_name

    class Meta:
        verbose_name = "Point"
        verbose_name_plural = "Points"


class Ambience(BaseModel):
    name = models.CharField(_("Name"), max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Ambience"
        verbose_name_plural = "Ambiences"
