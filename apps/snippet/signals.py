import logging

from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch.dispatcher import receiver

from apps.main.models import Restaurant
from apps.snippet.models import Category

logger = logging.getLogger(__name__)


# Function to clear cache whenever Category/Restaurant change
def clear_cache():
    cache.clear()
    logger.info("Global cache cleared due to Category/Restaurant change.")


# Signals to clear cache when Category or Restaurant changes
@receiver([post_save, post_delete], sender=Category)
@receiver([post_save, post_delete], sender=Restaurant)
def clear_category_cache_signal(sender, **kwargs):
    clear_cache()
    logger.info(f"Cache cleared due to changes in {sender.__name__} model.")
