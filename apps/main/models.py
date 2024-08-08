from django.db import models
from django.utils.translation import gettext_lazy as _

from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import StreamField, RichTextField
from wagtail.models import Page

from apps.main.blocks import FAQS, KeyPoint, WhyChooseUsCards, WinPlanCards, OurMissionVision


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
        on_delete=models.PROTECT,
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
        on_delete=models.PROTECT,
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
                FieldPanel("price_btn"),
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
        on_delete=models.PROTECT,
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
    ]
    subpage_types = []

    class Meta:
        verbose_name = "About Us"
        verbose_name_plural = "About Us"
