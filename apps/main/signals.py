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


# def clear_global_cache(reason: str):
#     cache.clear()
#     logger.info(f"Global cache cleared due to {reason}.")


# @page_published.connect
# def handle_restaurant_publish(sender, instance, **kwargs):
#     if instance.specific_class.__name__ == "Restaurant":
#         clear_global_cache(f'Restaurant publish event (title="{instance.title}", id={instance.id})')
#
#
# @page_unpublished.connect
# def handle_restaurant_unpublish(sender, instance, **kwargs):
#     if instance.specific_class.__name__ == "Restaurant":
#         clear_global_cache(f'Restaurant unpublish event (title="{instance.title}", id={instance.id})')
#
#
# @page_published.connect
# def handle_influencer_publish(sender, instance, **kwargs):
#     if instance.specific_class.__name__ == "Influencer":
#         clear_global_cache(f'Influencer publish event (title="{instance.title}", id={instance.id})')
#
#
# @page_unpublished.connect
# def handle_influencer_unpublish(sender, instance, **kwargs):
#     if instance.specific_class.__name__ == "Influencer":
#         clear_global_cache(f'Influencer unpublish event (title="{instance.title}", id={instance.id})')
#
#
# @receiver([post_save, post_delete], sender=Influencer)
# def handle_influencer_crud(sender, **kwargs):
#     clear_global_cache("Influencer model CRUD operation")