from wagtail.snippets.models import register_snippet

from .models import (Invitation, Review, Franchise, Reservation, BecomeInfluencer)

register_snippet(Invitation)
register_snippet(Review)
register_snippet(Franchise)
register_snippet(Reservation)
register_snippet(BecomeInfluencer)
