from wagtail.snippets.models import register_snippet

from .models import (Invitation, Review, Franchise, Reservation, BecomeInfluencer, OTPVerification, Notification,
                     NotificationPermission)

register_snippet(Invitation)
register_snippet(Review)
register_snippet(Franchise)
register_snippet(Reservation)
register_snippet(BecomeInfluencer)
register_snippet(OTPVerification)
register_snippet(Notification)
register_snippet(NotificationPermission)
