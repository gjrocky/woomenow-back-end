from django.urls import reverse, path
from wagtail import hooks
from wagtail.admin.menu import MenuItem
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet

from apps.main.views import SendEmailAdminView
from .models import (
    Invitation, Review, Franchise, BecomeInfluencer, OTPVerification,
    NotificationPermission, NotificationHistory, RestaurantMedia
)

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
    icon = "media"
    label = "restaurantmedia"
    menu_label = "Restaurant Media"
    base_url_path = "restaurant-media"


register_snippet(RestaurantMediaViewSet)


# --- Register your custom admin form view ---
@hooks.register("register_admin_views")
def register_send_email_admin_view():
    return [
        path("send-email/", SendEmailAdminView.as_view(), name="send_email_admin")
    ]


@hooks.register("register_admin_menu_item")
def register_send_email_menu_item():
    return MenuItem(
        "Send Email",
        reverse("send_email_admin"),
        icon_name="mail",
        order=10000,
    )
