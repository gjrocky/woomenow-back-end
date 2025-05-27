from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet

from .models import (Invitation, Review, Franchise, BecomeInfluencer, OTPVerification,
                     NotificationPermission, NotificationHistory, RestaurantMedia)

register_snippet(Invitation)
register_snippet(Review)
register_snippet(Franchise)
register_snippet(BecomeInfluencer)
register_snippet(OTPVerification)
register_snippet(NotificationPermission)
register_snippet(NotificationHistory)


class RestaurantMediaViewSet(SnippetViewSet):
    model = RestaurantMedia
    list_display = ['file', 'restaurants', 'created_at']
    search_fields = ['restaurants__name', 'restaurants__slug', 'restaurants__user__first_name']
    icon = "media"  # Optional icon
    label = "restaurantmedia"  # Unique label for internal use
    menu_label = "Restaurant Media"  # What shows in the sidebar
    base_url_path = "restaurant-media"  # Important for resolving URL


register_snippet(RestaurantMediaViewSet)
