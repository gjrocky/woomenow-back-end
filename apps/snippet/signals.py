import logging

from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch.dispatcher import receiver

from apps.main.models import Restaurant
from apps.snippet.models import Category

logger = logging.getLogger(__name__)


# Function to clear Category API cache
def clear_category_cache():
    deleted_count = cache.delete_pattern("category_api_*")
    if deleted_count:
        logger.info(f"Category API cache cleared ({deleted_count} keys).")
    else:
        logger.info("No Category API cache keys to clear.")


# Signals to clear cache when Category or Restaurant changes
@receiver([post_save, post_delete], sender=Category)
@receiver([post_save, post_delete], sender=Restaurant)
def clear_category_cache_signal(sender, **kwargs):
    clear_category_cache()
    logger.info(f"Cache cleared due to changes in {sender.__name__} model.")
