from wagtail.snippets.models import register_snippet

from .models import (Invitation, Review, Franchise, Reservation)

register_snippet(Invitation)
register_snippet(Review)
register_snippet(Franchise)
register_snippet(Reservation)
