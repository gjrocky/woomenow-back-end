from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet

from .forms import EmailTemplateForm
from .models import (
    Locality,
    City,
    State,
    Category,
    IPLocation, Contact, JoinTheWooForm, Ambience, CampaignTracker, Campaign, SiteVisit, PwaInstall, ParentCategory,
    EmailTemplate, EmailCategory, EmailTemplateChoice, GiveOffer,
)
from ..main.models import EmailExecution


class CityViewSet(SnippetViewSet):
    model = City
    list_display = ["name", "state", "modified_at"]
    list_per_page = 50
    inspect_view_enabled = False
    list_filter = {"state__name": ["icontains"]}
    search_fields = {"name": ["icontains"]}


class EmailTemplateViewSet(SnippetViewSet):
    model = EmailTemplate
    list_display = ["id", "name", "template", "subject", "has_tracking_link"]
    search_fields = ["name", "template", "subject"]
    list_filter = ["template__category", "has_tracking_link"]

    def get_form_class(self, obj=None, **kwargs):
        return EmailTemplateForm


class EmailCategoryViewSet(SnippetViewSet):
    model = EmailCategory
    list_display = ["name", "slug"]
    search_fields = ["name", "slug"]


class EmailTemplateChoiceViewSet(SnippetViewSet):
    model = EmailTemplateChoice
    list_display = ["label", "category", "choice_id"]
    list_filter = {"category": ["exact"]}
    search_fields = ["label"]


class EmailExecutionViewSet(SnippetViewSet):
    model = EmailExecution
    list_display = ["execution_id", "recipient_email", "recipient_name", "execution_flow", "started_at", "current_step",
                    "is_active", "last_sent_template_id", "is_opened"]
    list_filter = {"is_active": ["exact"], "current_step": ["exact"]}
    search_fields = ["recipient_email", "recipient_name"]

    readonly_fields = ["recipient_email", "recipient_name", "started_at", "current_step"]


class GiveOfferViewSet(SnippetViewSet):
    model = GiveOffer
    list_display = ["review", "message", "created_at"]
    search_fields = ["review"]


register_snippet(CityViewSet)
register_snippet(Locality)
register_snippet(State)
register_snippet(Category)
register_snippet(ParentCategory)
register_snippet(IPLocation)
register_snippet(Contact)
register_snippet(JoinTheWooForm)
register_snippet(Ambience)
register_snippet(Campaign)
register_snippet(CampaignTracker)
register_snippet(SiteVisit)
register_snippet(PwaInstall)
register_snippet(EmailTemplateViewSet)
register_snippet(EmailCategoryViewSet)
register_snippet(EmailTemplateChoiceViewSet)
register_snippet(EmailExecutionViewSet)
register_snippet(GiveOfferViewSet)
