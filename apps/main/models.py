import html

from bs4 import BeautifulSoup
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import JSONField, SET_NULL
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalManyToManyField
from wagtail import blocks
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.blocks import URLBlock
from wagtail.fields import StreamField, RichTextField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Page

from apps.main.blocks import FAQS, KeyPoint, WhyChooseUsCards, WinPlanCards, OurMissionVision, PricingCard, \
    ReadyToElevateBlock, TermsOfServiceBlock, PrivacyPolicyBlock, DiamondStatusBlock, ReviewSystemBlock
from apps.main.choices import RestaurantType, BudgetType
from apps.main.helper import email_dict
from apps.snippet.models import BaseModel
from send_email import send_email

CustomUser = get_user_model()


class HomePage(Page):
    max_count = 1
    hero_heading = RichTextField(_("Main Heading"), max_length=500, help_text="Hero Heading")
    hero_description = RichTextField(_("Main Description"), max_length=1000, help_text="Hero Description")

    dining_heading = RichTextField(_("Dining Heading"), max_length=500, help_text="Dining Heading")
    dining_info = RichTextField(_("Dining Information"), max_length=1000, help_text="Dining Info")

    experience_heading = RichTextField(_("Experience Heading"), max_length=500, help_text="Experience Heading")
    experience_info = RichTextField(_("Experience Information"), max_length=1000, help_text="Experience Info")

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel("hero_heading"),
            FieldPanel("hero_description"),
        ], heading="Hero Section", classname="collapsible collapsed"),

        MultiFieldPanel([
            FieldPanel("dining_heading"),
            FieldPanel("dining_info"),
        ], heading="Dining Section", classname="collapsible collapsed"),

        MultiFieldPanel([
            FieldPanel("experience_heading"),
            FieldPanel("experience_info"),
        ], heading="Experience Section", classname="collapsible collapsed"),
    ]

    class Meta:
        verbose_name = "Home Page"
        verbose_name_plural = "Home Pages"


class FAQs(Page):
    max_count = 1
    faq = StreamField([("que_and_ans", FAQS())], min_num=3, use_json_field=True)
    content_panels = Page.content_panels + [FieldPanel("faq")]
    subpage_types = []

    class Meta:
        verbose_name = "FAQs"
        verbose_name_plural = "FAQs"


class Business(Page):
    CTA_btn = RichTextField(_("CTA Button"), blank=True, null=True)
    CTA_btn_icon = models.ForeignKey(
        "wagtailimages.Image",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="+",
    )

    heading = RichTextField(_("Heading"), blank=True, null=True, max_length=100)
    description = RichTextField(_("Description"), blank=True, null=True, max_length=1000)
    video_1 = models.FileField(
        _("Video 1"), blank=True, null=True, upload_to="video/business/"
    )
    video_2 = models.FileField(
        _("Video 2"), blank=True, null=True, upload_to="video/business/"
    )
    video_3 = models.FileField(
        _("Video 3"), blank=True, null=True, upload_to="video/business/"
    )
    key_point = StreamField(
        [
            ("key_point", KeyPoint()),
        ],
        min_num=3,
        max_num=3,
        use_json_field=True,
    )

    choose_heading = RichTextField(_("Heading"), blank=True, null=True)
    choose_description = RichTextField(_("Description"), blank=True, null=True)
    choose_image = models.ForeignKey(
        "wagtailimages.Image",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="+",
    )
    why_choose_us_cards = StreamField(
        [("cards", WhyChooseUsCards())], null=True, blank=True, use_json_field=True
    )

    win_plan_heading = RichTextField(_("Heading"), blank=True, null=True)
    win_plan_description = RichTextField(_("Description"), blank=True, null=True)
    win_plan_cards = StreamField(
        [("cards", WinPlanCards())], null=True, blank=True, use_json_field=True
    )

    price_heading = RichTextField(_("Heading"), blank=True, null=True)
    price_description = RichTextField(_("Description"), blank=True, null=True)
    price_btn = RichTextField(_("Button"), blank=True, null=True)

    faq = StreamField([("que_and_ans", FAQS())], min_num=3, use_json_field=True)

    ready_to_elevate_section = StreamField(
        [("ready_to_elevate", ReadyToElevateBlock())],
        use_json_field=True,
    )

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("CTA_btn"),
                FieldPanel("CTA_btn_icon"),
            ],
            heading="Extra Content",
            classname="collapsible collapsed",
        ),
        MultiFieldPanel(
            [
                FieldPanel("heading"),
                FieldPanel("description"),
                FieldPanel("video_1"),
                FieldPanel("video_2"),
                FieldPanel("video_3"),
                FieldPanel("key_point"),
            ],
            heading="Hero Section",
            classname="collapsible collapsed",
        ),
        MultiFieldPanel(
            [
                FieldPanel("choose_heading"),
                FieldPanel("choose_description"),
                FieldPanel("choose_image"),
                FieldPanel("why_choose_us_cards"),
            ],
            heading="Why choose Us Section",
            classname="collapsible collapsed",
        ),
        MultiFieldPanel(
            [
                FieldPanel("win_plan_heading"),
                FieldPanel("win_plan_description"),
                FieldPanel("win_plan_cards"),
            ],
            heading="Winning Plan Section",
            classname="collapsible collapsed",
        ),
        MultiFieldPanel(
            [
                FieldPanel("price_heading"),
                FieldPanel("price_description"),
                FieldPanel("price_btn"),
            ],
            heading="Pricing Section",
            classname="collapsible collapsed",
        ),
        MultiFieldPanel(
            [FieldPanel("faq")],
            heading="FAQs Section",
            classname="collapsible collapsed",
        ),
        MultiFieldPanel(
            [
                FieldPanel("ready_to_elevate_section"),
            ],
            heading="Ready To Elevate Section",
            classname="collapsible collapsed",
        ),
    ]
    subpage_types = []

    max_count = 1

    class Meta:
        verbose_name = "business"
        verbose_name_plural = "business"


class About(Page):
    max_count = 1
    vision_points = StreamField(
        [("mission_and_vision", OurMissionVision())], min_num=3, use_json_field=True
    )
    image = models.ForeignKey(
        "wagtailimages.Image",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    description = RichTextField(
        _("Description"),
        blank=True,
        null=True,
        max_length=2000,
        help_text="Main Description",
    )
    heading = RichTextField(
        _("Heading"), blank=True, null=True, max_length=2000, help_text="Main Heading"
    )
    vision_title = RichTextField(_("Title"), max_length=500)

    ready_to_elevate_section = StreamField(
        [("ready_to_elevate", ReadyToElevateBlock())],
        use_json_field=True,
    )

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("heading"),
                FieldPanel("description"),
                FieldPanel("image"),
            ],
            "Hero Section",
        ),
        MultiFieldPanel(
            [
                FieldPanel("vision_title"),
                FieldPanel("vision_points"),
            ],
            "Vision Points Section",
        ),
        MultiFieldPanel(
            [
                FieldPanel("ready_to_elevate_section"),
            ],
            heading="Ready To Elevate Section",
            classname="collapsible collapsed",
        ),
    ]
    subpage_types = []

    class Meta:
        verbose_name = "About Us"
        verbose_name_plural = "About Us"


class Pricing(Page):
    max_count = 1

    heading = RichTextField(_("Heading"), blank=True, null=True, max_length=100)
    description = RichTextField(_("Description"), blank=True, null=True, max_length=1000)
    note = RichTextField(_("Note"), blank=True, null=True, max_length=1000)
    CTA_btn = RichTextField(_("CTA Button"), blank=True, null=True)
    cards = StreamField(
        [("cards", PricingCard())], use_json_field=True
    )
    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("heading"),
                FieldPanel("description"),
                FieldPanel("note"),
                FieldPanel("CTA_btn"),
            ],
            heading="Main Content",
            classname="collapsible collapsed",
        ),
        MultiFieldPanel(
            [
                FieldPanel("cards"),
            ],
            heading="pricing Content",
            classname="collapsible collapsed",
        ),
    ]
    subpage_types = []

    class Meta:
        verbose_name = "Pricing"
        verbose_name_plural = "Pricing"


class InfluencerListing(Page):
    max_count = 1
    subpage_types = ['influencer']

    class Meta:
        verbose_name = "Influencer Listing"
        verbose_name_plural = "Influencer Listing"


class Influencer(Page):
    profile = models.ForeignKey(
        "wagtailimages.Image",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    name = RichTextField(_("Name"), max_length=500)
    user = models.OneToOneField(CustomUser, on_delete=models.PROTECT, related_name='influencer')
    description = RichTextField(_("Description"), blank=True, null=True, max_length=10000)
    social_links = StreamField([('link', URLBlock())], use_json_field=True, null=True, blank=True)
    city = models.ForeignKey('snippet.City', on_delete=models.SET_NULL, null=True, blank=True,
                             related_name="influencers")
    restaurant_images = StreamField([('image', ImageChooserBlock())], null=True, blank=True, use_json_field=True)
    parent_page_types = ['InfluencerListing']

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("name"),
                FieldPanel("profile"),
                FieldPanel("description"),
                FieldPanel("city"),
                FieldPanel("restaurant_images"),
                FieldPanel("user"),
                FieldPanel("social_links"),
            ],
            heading="Influencer Content",
            classname="collapsible collapsed",
        ),
    ]

    class Meta:
        verbose_name = "Influencer"
        verbose_name_plural = "Influencers"

    def get_text(self, text):
        return BeautifulSoup(text, "html.parser").get_text()

    def save(self, *args, **kwargs):
        if not self.pk:
            e = [self.user.email]
            body = 'emails/become-an-influencer.html'
            context = dict(name=self.get_text(self.name), **email_dict)
            subject_context = dict(subject='Welcome to the WooMeNow Influencer Community!')
            send_email(e, body, context, subject_context)
        super().save(*args, **kwargs)

    def __str__(self):
        plain_name = self.get_text(self.name)
        email = self.user.email or ""
        return f"{html.unescape(plain_name)} ({email})"


class JoinTheWoo(Page):
    max_count = 1
    subpage_types = []

    heading = RichTextField(
        _("Heading"), max_length=500, help_text="Main Heading"
    )
    description = RichTextField(
        _("Short Description"),
        max_length=500,
        help_text="Short Description",
    )
    about_community = RichTextField(_('Description'), max_length=2000, help_text="Main Description")
    sub_heading = RichTextField(_('Sub Heading'), max_length=500)
    community_points = StreamField(
        [("point", blocks.RichTextBlock(required=True, max_length=2000, help_text='Block Title'))], min_num=3,
        use_json_field=True
    )

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("heading"),
                FieldPanel("description"),
                FieldPanel("about_community"),
                FieldPanel("sub_heading"),
                FieldPanel("community_points"),
            ],
            heading="Join The Woo Content",
            classname="collapsible collapsed",
        ),
    ]

    class Meta:
        verbose_name = "Join The Woo"
        verbose_name_plural = "Join The Woo"


class Invitation(BaseModel):
    restaurant_name = models.TextField(_("Restaurant Name"), max_length=500)
    location = models.CharField(_("Location"), max_length=255)
    invited_by = models.ForeignKey('Influencer', on_delete=models.SET_NULL, null=True, blank=True)
    invite_to = models.EmailField(_("Invite To"), max_length=255)
    type = models.CharField('Restaurant Type', choices=RestaurantType.choices, max_length=255)
    google_link = models.URLField(_("Google Link"), max_length=255, blank=True, null=True)
    phone = models.CharField(_("Phone Number"), max_length=255)
    super_user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)

    panels = [
        FieldPanel("restaurant_name"),
        FieldPanel("location"),
        FieldPanel("invited_by"),
        FieldPanel("invite_to"),
        FieldPanel("type"),
        FieldPanel("google_link"),
        FieldPanel("phone"),
    ]

    def __str__(self):
        return self.invite_to

    class Meta:
        verbose_name = "Invitation"
        verbose_name_plural = "Invitations"


class Review(BaseModel):
    content = models.TextField(_("Content"), max_length=5000, null=True, blank=True)
    rating = models.DecimalField(_("Rating"), blank=True, null=True, max_digits=5, decimal_places=4)
    more_info = models.JSONField(_('More Information'), null=True, blank=True)
    is_verified = models.BooleanField(_("Is Verified"), default=False)
    is_published = models.BooleanField(_("Is Published"), default=False)
    posted_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    bill = models.ForeignKey(
        "wagtailimages.Image",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    images = StreamField([('image', ImageChooserBlock())], use_json_field=True, null=True, blank=True)
    restaurant = models.ForeignKey('Restaurant', on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='reviews')
    approved_by = models.OneToOneField('Influencer', on_delete=models.SET_NULL, null=True, blank=True, )
    panels = [
        FieldPanel("posted_by"),
        FieldPanel("content"),
        FieldPanel("rating"),
        FieldPanel("is_verified"),
        FieldPanel("is_published"),
        FieldPanel("more_info"),
        FieldPanel("bill"),
        FieldPanel("images"),
        FieldPanel("restaurant"),
    ]

    def save(self, *args, **kwargs):
        if not self.is_verified and int(self.rating) >= 3:
            self.is_published = True
        super().save(*args, **kwargs)

    def __str__(self):
        return self.posted_by.first_name

    class Meta:
        verbose_name = "Review"
        verbose_name_plural = "Reviews"


class Franchise(BaseModel):
    name = models.CharField(_("Name"), max_length=255)

    panels = [
        FieldPanel("name"),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Franchise"
        verbose_name_plural = "Franchise"


def default_reservation_time():
    return {"reservation": {}}


class RestaurantListing(Page):
    max_count = 1
    subpage_types = ['Restaurant']

    class Meta:
        verbose_name = "Restaurant Listing"
        verbose_name_plural = "Restaurant Listing"


class Restaurant(Page):
    name = RichTextField(_("Name"), max_length=500)
    short_description = RichTextField(_("Short Description"), max_length=2000)
    about_restaurant = RichTextField(_("About"), max_length=10000, null=True, blank=True)
    email = models.EmailField(_("Email"), max_length=255, null=True, blank=True)
    phone_number = models.TextField(_('Phone Number'), blank=True, null=True)
    location = models.TextField(_("Location"), max_length=2000, blank=True, null=True)
    is_franchise = models.BooleanField(_("Is Franchise"), default=False)
    franchise = models.ForeignKey('Franchise', on_delete=models.SET_NULL, null=True, blank=True)
    menus = StreamField([('menu', ImageChooserBlock())], use_json_field=True, null=True, blank=True)
    invited_by = models.ForeignKey('Influencer', on_delete=models.SET_NULL, null=True, blank=True)
    recommended_by = ParentalManyToManyField(CustomUser, related_name='Restaurants')
    type = models.CharField(_('Restaurant Type'), max_length=255, choices=RestaurantType.choices)
    categories = ParentalManyToManyField("snippet.Category", blank=True, related_name="Restaurants")
    city = models.ForeignKey("snippet.City", on_delete=models.SET_NULL, related_name="Restaurants", null=True,
                             blank=True)
    is_featured = models.BooleanField(_("Featured Place"), default=False)
    is_home_featured = models.BooleanField(_("Home Featured Place"), default=False)
    restaurant_images = StreamField([('image', ImageChooserBlock())], use_json_field=True)
    rating = models.DecimalField(_("Rating"), blank=True, null=True, max_digits=5, decimal_places=4)
    website_url = models.URLField(_("Website URL"), null=True, blank=True)
    profile_pic = models.ForeignKey(
        "wagtailimages.Image",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="+",
    )
    reservation_time = JSONField(_("Reservation Time"), blank=True, null=True, default=default_reservation_time)
    budget_friendly = models.CharField(_('Restaurant Type'), max_length=255, choices=BudgetType.choices,
                                       default=BudgetType.INEXPENSIVE)
    ambience = ParentalManyToManyField("snippet.Ambience", blank=True, related_name="Restaurants")
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='restaurants')
    address = models.TextField(_("Address"), max_length=2000, blank=True, null=True)
    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("user"),
                FieldPanel("profile_pic"),
                FieldPanel("name"),
                FieldPanel("short_description"),
                FieldPanel("about_restaurant"),
                FieldPanel("email"),
                FieldPanel("phone_number"),
                FieldPanel("location"),
                FieldPanel("address"),
            ],
            "Restaurant Details",
        ),
        MultiFieldPanel(
            [
                FieldPanel("type"),
                FieldPanel("categories"),
                FieldPanel("city"),
                FieldPanel("menus"),
                FieldPanel("restaurant_images"),
                FieldPanel("recommended_by"),
            ],
            "Information",
        ),
        MultiFieldPanel(
            [
                FieldPanel("ambience"),
                FieldPanel("reservation_time"),
                FieldPanel("is_franchise"),
                FieldPanel("franchise"),
                FieldPanel("rating"),
                FieldPanel("website_url"),
                FieldPanel("invited_by"),
                FieldPanel("is_featured"),
                FieldPanel("is_home_featured"),
            ],
            "Additional Information",
        ),
    ]
    parent_page_types = ['RestaurantListing']

    def __str__(self):
        clean_name = strip_tags(self.name)
        unescaped_name = html.unescape(clean_name)
        return f"{unescaped_name}"

    class Meta:
        verbose_name = "Restaurant"
        verbose_name_plural = "Restaurants"


class Reservation(BaseModel):
    customer = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.SET_NULL, null=True, blank=True)
    emergency_contact = models.CharField(_("Emergency Contact"), max_length=255, null=True, blank=True)
    timing = models.DateTimeField(_("Timing"))
    people = models.IntegerField(_("No of Guest"), default=0)

    panels = [
        FieldPanel("customer"),
        FieldPanel("restaurant"),
        FieldPanel("emergency_contact"),
        FieldPanel("timing"),
        FieldPanel("people"),
    ]

    def __str__(self):
        return self.restaurant.name

    class Meta:
        verbose_name = "Reservation"
        verbose_name_plural = "Reservations"


class BecomeInfluencer(BaseModel):
    user = models.OneToOneField(CustomUser, on_delete=models.PROTECT, related_name='become_an_influencer')
    insta_link = models.URLField(_('Instagram'), null=True, blank=True)
    tiktok_link = models.URLField(_('TikTok'), null=True, blank=True)
    other_link = models.URLField(_('Other'), null=True, blank=True)

    panels = [
        FieldPanel("user"),
        FieldPanel("insta_link"),
        FieldPanel("tiktok_link"),
        FieldPanel("other_link"),
    ]

    def __str__(self):
        return self.user.first_name

    class Meta:
        verbose_name = "Become Influencer"
        verbose_name_plural = "Become Influencers"


class OTPVerification(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    expires_at = models.DateTimeField(default=now)

    def is_valid(self):
        return now() < self.expires_at


class NotificationPermission(BaseModel):
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
                             related_name='notification_permission')
    endpoint = models.TextField(_('Endpoint'), max_length=255, null=True, blank=True)
    p256dh = models.CharField(max_length=255, null=True, blank=True)
    auth = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f'{self.id}'

    class Meta:
        verbose_name = "Notification Permission"
        verbose_name_plural = "Notification Permissions"


class NotificationHistory(BaseModel):
    title = models.CharField(_('Title'), max_length=255)
    description = models.TextField(_('Description'), max_length=2000)
    image = models.ForeignKey(
        "wagtailimages.Image",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="+",
    )
    send_to = models.CharField(_('Send To'), max_length=255)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Notification History"
        verbose_name_plural = "Notification Histories"


class RestaurantMedia(BaseModel):
    file = models.FileField(upload_to='media/')
    restaurants = models.ForeignKey('Restaurant', on_delete=SET_NULL, null=True, blank=True, related_name='media')

    def __str__(self):
        return self.file.name

    class Meta:
        verbose_name = "Restaurant Media"
        verbose_name_plural = "Restaurant Media"


def get_text(text):
    if not text:
        return ""
    return BeautifulSoup(text, "html.parser").get_text()


class TermsOfService(Page):
    max_count = 1
    effective_date = models.DateField(_("Effective Date"), null=True, blank=True)
    page_title = RichTextField(_("Title"))
    description = RichTextField(_("Description"), null=True, blank=True)
    terms_section = StreamField([("terms_section", TermsOfServiceBlock())], min_num=1, use_json_field=True)
    contact_us = RichTextField(_("Contact Us"), blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("effective_date"),
        FieldPanel("page_title"),
        FieldPanel("description"),
        FieldPanel("terms_section"),
        FieldPanel("contact_us"),
    ]

    class Meta:
        verbose_name = "Terms of Service Page"


class PrivacyPolicy(Page):
    max_count = 1
    effective_date = models.DateField(_("Effective Date"), null=True, blank=True)
    page_title = RichTextField(_("Title"))
    description = RichTextField(_("Description"), null=True, blank=True)
    policy_section = StreamField([("policy_section", PrivacyPolicyBlock())], min_num=1, use_json_field=True)
    contact_us = RichTextField(_("Contact Us"), blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("effective_date"),
        FieldPanel("page_title"),
        FieldPanel("description"),
        FieldPanel("policy_section"),
        FieldPanel("contact_us"),
    ]

    class Meta:
        verbose_name = "Privacy Policy Page"


class DiamondStatus(Page):
    max_count = 1
    page_title = RichTextField(_("Title"))
    description = RichTextField(_("Description"), null=True, blank=True)
    diamond_status_section = StreamField([("diamond_section", DiamondStatusBlock())], min_num=1, use_json_field=True)

    content_panels = Page.content_panels + [
        FieldPanel("page_title"),
        FieldPanel("description"),
        FieldPanel("diamond_status_section"),
    ]

    class Meta:
        verbose_name = "Diamond Status Page"


class ReviewSystem(Page):
    max_count = 1
    page_title = RichTextField(_("Title"))
    description = RichTextField(_("Description"), null=True, blank=True)
    review_section = StreamField([("review_section", ReviewSystemBlock())], min_num=1, use_json_field=True)

    content_panels = Page.content_panels + [
        FieldPanel("page_title"),
        FieldPanel("description"),
        FieldPanel("review_section"),
    ]

    class Meta:
        verbose_name = "Review System Page"


# Email Automation Model
class EmailExecution(models.Model):
    recipient_email = models.EmailField()
    recipient_name = models.CharField(max_length=255)
    started_at = models.DateTimeField(default=timezone.now)
    current_step = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.recipient_email} - Step {self.current_step}"
