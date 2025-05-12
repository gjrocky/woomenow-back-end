from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet

from .models import (
    Locality,
    City,
    State,
    Category,
    IPLocation, Contact, JoinTheWooForm, Ambience, CampaignTracker, Campaign, SiteVisit, PwaInstall,
)


class CityViewSet(SnippetViewSet):
    model = City
    list_display = ["name", "state", "modified_at"]
    list_per_page = 50
    inspect_view_enabled = False
    list_filter = {"state__name": ["icontains"]}
    search_fields = {"name": ["icontains"]}


register_snippet(CityViewSet)
register_snippet(Locality)
register_snippet(State)
register_snippet(Category)
register_snippet(IPLocation)
register_snippet(Contact)
register_snippet(JoinTheWooForm)
register_snippet(Ambience)
register_snippet(Campaign)
register_snippet(CampaignTracker)
register_snippet(SiteVisit)
register_snippet(PwaInstall)
