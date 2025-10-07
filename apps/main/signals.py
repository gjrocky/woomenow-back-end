import logging

from django.core.cache import cache
from django.db.models import Avg
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from wagtail.signals import page_published, page_unpublished

from apps.main.models import Review, Influencer

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Review)
def handle_review_save(sender, instance, created, **kwargs):
    if instance.is_published and not instance.is_verified:
        instance.posted_by.point = instance.posted_by.point + 20
        instance.posted_by.save()

    try:
        average_rating = instance.restaurant.reviews.filter(is_published=True).aggregate(
            avg_rating=Avg('rating')
        )['avg_rating']
        if average_rating is not None:
            average_rating = round(average_rating, 2)
            instance.restaurant.rating = average_rating
            instance.restaurant.save(update_fields=['rating'])
    except AttributeError as e:
        print(f"Error updating restaurant rating: {e}")


def clear_restaurant_cache():
    deleted_count = cache.delete_pattern("restaurant_api_*")
    if deleted_count:
        logger.info(f"Restaurant API cache cleared ({deleted_count} keys).")
    else:
        logger.info("No Restaurant API cache keys to clear.")


# Connect signals
@page_published.connect
def clear_cache_on_publish(sender, instance, **kwargs):
    if instance.specific_class.__name__ == "Restaurant":
        clear_restaurant_cache()
        logger.info(f'Published Restaurant Page: "{instance.title}" id={instance.id}')


@page_unpublished.connect
def clear_cache_on_unpublish(sender, instance, **kwargs):
    if instance.specific_class.__name__ == "Restaurant":
        clear_restaurant_cache()
        logger.info(f'Unpublished Restaurant Page: "{instance.title}" id={instance.id}')


def clear_influencer_cache():
    deleted_count = cache.delete_pattern("influencer_api_*")
    if deleted_count:
        logger.info(f"Influencer API cache cleared ({deleted_count} keys).")
    else:
        logger.info("No Influencer API cache keys to clear.")


@page_published.connect
def clear_cache_on_publish(sender, instance, **kwargs):
    if instance.specific_class.__name__ == "Influencer":
        clear_influencer_cache()
        logger.info(f'Published Influencer Page: "{instance.title}" id={instance.id}')


@page_unpublished.connect
def clear_cache_on_unpublish(sender, instance, **kwargs):
    if instance.specific_class.__name__ == "Influencer":
        clear_influencer_cache()
        logger.info(f'Unpublished Influencer Page: "{instance.title}" id={instance.id}')
