import urllib.parse

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import OneToOneField, TextField
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.search import index

from apps.snippet.choices import OFFER_CHOICES

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


class ParentCategory(BaseModel):
    name = models.TextField(_("Name"), max_length=50)
    slug = models.TextField(_("Slug"), max_length=100, unique=True)

    panels = [
        FieldPanel("name"),
    ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Parent Category"
        verbose_name_plural = "Parent Categories"


class Category(BaseModel):
    name = models.TextField(_("Name"), max_length=50)
    image = models.ForeignKey(
        "wagtailimages.Image",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="+")
    slug = models.TextField(_("Slug"), max_length=100, unique=True)
    parent_category = models.ForeignKey("ParentCategory", on_delete=models.CASCADE, related_name="categories")

    panels = [
        FieldPanel("name"),
        FieldPanel("image"),
        FieldPanel('parent_category')
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
    category = models.CharField(_("Category"), max_length=100, null=True, blank=True)
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


class SiteVisit(models.Model):
    user_identifier = models.CharField(max_length=255, unique=True)
    user_agent = models.CharField(max_length=500, blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    first_visit = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user_identifier


class PwaInstall(models.Model):
    user_identifier = models.CharField(max_length=255, unique=True)  # User ID or email
    user_agent = models.TextField(blank=True, null=True)  # Store the user agent
    ip_address = models.GenericIPAddressField(blank=True, null=True)  # Store the IP address
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user_identifier


class EmailCategory(models.Model):
    name = models.CharField(_("Category Name"), max_length=255, unique=True)
    slug = models.SlugField(_("Slug"), max_length=255, unique=True)

    panels = [
        FieldPanel("name"),
        FieldPanel("slug"),
    ]

    class Meta:
        verbose_name = "Email Category"
        verbose_name_plural = "Email Categories"

    def __str__(self):
        return self.name


class EmailTemplateChoice(models.Model):
    category = models.ForeignKey(EmailCategory, on_delete=models.CASCADE, related_name="templates",
                                 verbose_name="Category")
    choice_id = models.PositiveIntegerField(editable=False)
    label = models.CharField(_("Template Label"), max_length=255)

    panels = [
        FieldPanel("category"),
        FieldPanel("label"),
    ]

    class Meta:
        verbose_name = "Email Template Choice"
        verbose_name_plural = "Email Template Choices"
        unique_together = ("category", "choice_id")
        ordering = ["category", "choice_id"]

    def __str__(self):
        return f"{self.label} ({self.category.name})"

    def save(self, *args, **kwargs):
        if not self.pk:  # Assign ID only on creation
            last_id = (
                EmailTemplateChoice.objects.filter(category=self.category)
                .aggregate(models.Max("choice_id"))
                .get("choice_id__max")
            )
            self.choice_id = (last_id or 0) + 1
        super().save(*args, **kwargs)


class EmailTemplate(models.Model):
    template = models.ForeignKey(
        EmailTemplateChoice,
        on_delete=models.PROTECT,
        related_name="email_templates",
        help_text="Please select an Email Template.",
    )
    name = models.CharField(max_length=255, unique=True, help_text="Enter a unique name for your Email Template.")
    subject = models.CharField(max_length=255, help_text="Enter the subject of your Email Template.")
    rich_body = RichTextField(
        features=['h1', 'h2', 'h3', 'bold', 'italic', 'ol', 'ul', 'hr', 'link', 'document-link', 'image', 'embed',
                  'code'], default='', help_text="Enter content of your Email Template.")
    rich_lower_body = RichTextField(
        features=['h1', 'h2', 'h3', 'bold', 'italic', 'ol', 'ul', 'hr', 'link', 'document-link', 'image', 'embed',
                  'code'], default='', blank=True,
        help_text="Only use this if Email has a hardcoded section, add content after hardcoded section here.")
    has_tracking_link = models.BooleanField(default=False)

    panels = [
        FieldPanel("template"),
        FieldPanel("name"),
        FieldPanel("subject"),
        FieldPanel("rich_body"),
        FieldPanel("rich_lower_body"),
        FieldPanel("has_tracking_link")
    ]

    def __str__(self):
        return self.name


class GiveOffer(models.Model):
    review = models.ForeignKey("main.Review", on_delete=models.SET_NULL, null=True, blank=True)
    message = models.TextField(_("Message"), max_length=500)
    goodwill_offer = models.CharField(max_length=100, choices=OFFER_CHOICES, blank=True, null=True,
                                      help_text="Optional Goodwill Gesture")
    custom_offer = models.TextField(_("Custom Offer"), blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    panels = [
        FieldPanel("review"),
        FieldPanel("message"),
        FieldPanel("goodwill_offer"),
        FieldPanel("custom_offer"),
    ]

    def __str__(self):
        if self.review:
            user = getattr(self.review.posted_by, "first_name", self.review.posted_by) or "Unknown User"
            restaurant = getattr(self.review.restaurant, "name", self.review.restaurant) or "Unknown Restaurant"
            return f"Offer for {user} from {restaurant}"
        return "Offer (no review linked)"

    class Meta:
        verbose_name = "Give Offer"
        verbose_name_plural = "Give Offers"
