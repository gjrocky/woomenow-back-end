from django.db import models
from django.utils.translation import gettext_lazy as _


class RestaurantType(models.TextChoices):
    DINING = 'dining', _("Dining")
    EXPERIENCE = 'experience', _("Experience")
