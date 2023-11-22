import pytest
from django.contrib.auth.models import User
from books.models import ReadingProfile, ReadingSession
from django.db.models.signals import post_save
from django.test import TestCase
from django.dispatch import Signal

from books.signals import create_reading_profile

from datetime import timedelta


@pytest.mark.django_db(transaction=True)
class TestReadingProfileSignal:

    def test_create_reading_profile_signal(self):
        assert User.objects.count() == 0
        assert ReadingProfile.objects.count() == 0

        user = User.objects.create_user(username="testuser")

        assert User.objects.count() == 1
        assert ReadingProfile.objects.count() == 1

        assert User.objects.first().readingprofile is not None
        assert User.objects.first().username == "testuser"
        assert ReadingProfile.objects.first().user == user

    def test_update_daily_reading_profile(self, user, reading_profile):
        assert reading_profile.reading_last_week == timedelta(0)
        assert reading_profile.reading_last_month == timedelta(0)
        assert reading_profile.last_day_total_reading_time == timedelta(0)
        assert reading_profile.daily_reading_time == []
        assert user.readingsession_set.count() == 0
        assert user.readingsession_set.count() == 0
        assert ReadingSession.get_user_all_books_total_reading_time(user) == timedelta(0)


        # # Simulate a week of reading an hour per day
        # user.readingprofile.daily_reading_time = [timedelta(hours=1)] * 7
        # user.readingprofile.save()
        #
        # # Update the reading profile
        # user.readingprofile.update_daily_reading_profile()
        #
        # # Check the data has been updated correctly
        # assert user.readingprofile.reading_last_week == timedelta(hours=7)
        # assert user.readingprofile.reading_last_month == timedelta(hours=7)
        #
        # # Simulate another 23 days of reading an hour per day
        # user.readingprofile.daily_reading_time += [timedelta(hours=1)] * 23
        # user.readingprofile.save()
        #
        # # Update the reading profile again
        # user.readingprofile.update_daily_reading_profile()
        #
        # # Check data again
        # assert user.readingprofile.reading_last_week == timedelta(hours=7)  # Last 7 days only
        # assert user.readingprofile.reading_last_month == timedelta(hours=30)  # Last 30 days only
