from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import ReadingProfile


@receiver(post_save, sender=User)
def create_reading_profile(sender, instance, created, **kwargs):
    if created:
        ReadingProfile.objects.create(user=instance)
