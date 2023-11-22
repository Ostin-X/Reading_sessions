import logging

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import ReadingProfile


@receiver(post_save, sender=User)
def create_reading_profile(sender, instance, created, **kwargs):
    """
    Signal function to be called after a User instance is saved.

    Creates an associated ReadingProfile instance whenever a new User instance is created.

    :param sender: The model class. (User)
    :param instance: The actual instance being saved.
    :param created: Boolean; True if a new record was created.
    :param kwargs: Any other parameters.

    :return: None
    """
    if created:
        try:
            ReadingProfile.objects.create(user=instance)
        except Exception as e:
            logging.error(f"Error creating Reading Profile for user {instance.username}: {type(e).__name__}, {e}")
