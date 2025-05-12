from wagtail.snippets.models import register_snippet

from .models import (Invitation, Review, Franchise, BecomeInfluencer, OTPVerification,
                     NotificationPermission, NotificationHistory)

register_snippet(Invitation)
register_snippet(Review)
register_snippet(Franchise)
register_snippet(BecomeInfluencer)
register_snippet(OTPVerification)
register_snippet(NotificationPermission)
register_snippet(NotificationHistory)
