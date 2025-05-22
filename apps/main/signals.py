from django.db.models import Avg
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.main.models import Review


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
