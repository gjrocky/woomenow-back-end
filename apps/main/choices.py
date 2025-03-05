from django.db import models
from django.utils.translation import gettext_lazy as _


class RestaurantType(models.TextChoices):
    DINING = 'dining', _("Dining")
    EXPERIENCE = 'experience', _("Experience")


class BudgetType(models.TextChoices):
    INEXPENSIVE = 'inexpensive', _("Inexpensive")
    MODERATELY_EXPENSIVE = 'moderately_expensive', _("Moderately Expensive")
    EXPENSIVE = 'expensive', _("Expensive")
