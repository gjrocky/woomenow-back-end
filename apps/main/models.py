from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail.models import Page

from apps.main.blocks import FAQS


class FAQs(Page):
    max_count = 1
    faq = StreamField([("que_and_ans", FAQS())], min_num=3, use_json_field=True)
    content_panels = Page.content_panels + [FieldPanel("faq")]
    subpage_types = []

    class Meta:
        verbose_name = "FAQs"
        verbose_name_plural = "FAQs"
