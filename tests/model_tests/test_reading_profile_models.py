from datetime import timedelta
from unittest.mock import patch

import pytest
from django.contrib.auth.models import User

from books.models import ReadingProfile


@pytest.mark.django_db(transaction=True)
class TestReadingProfileModel:

    def test_create_reading_profile_signal(self):
        assert User.objects.count() == 0
        assert ReadingProfile.objects.count() == 0

        user = User.objects.create_user(username="testuser")

        assert User.objects.count() == 1
        assert ReadingProfile.objects.count() == 1

        assert User.objects.first().readingprofile is not None
        assert User.objects.first().username == "testuser"
        assert ReadingProfile.objects.first().user == user

    def test_update_daily_reading_profile(self, user):
        reading_profile = user.readingprofile

        assert reading_profile.reading_last_week == timedelta(0)
        assert reading_profile.reading_last_month == timedelta(0)
        assert reading_profile.last_day_total_reading_time == timedelta(0)
        assert reading_profile.daily_reading_time == []

        with patch('books.models.ReadingSession.get_user_all_books_total_reading_time',
                   side_effect=[timedelta(seconds=n) for n in range(1, 35)]):
            for i in range(1, 11):

                i_history_timedelta_list = [timedelta(seconds=1)] * i

                reading_profile.update_daily_reading_profile()

                if i <= 7:
                    assert reading_profile.reading_last_week == timedelta(seconds=i)
                assert reading_profile.reading_last_week <= timedelta(seconds=7)

                if i <= 30:
                    assert reading_profile.reading_last_month == timedelta(seconds=i)
                assert reading_profile.reading_last_month <= timedelta(seconds=30)

                assert reading_profile.last_day_total_reading_time == timedelta(seconds=i)
                assert reading_profile.daily_reading_time == i_history_timedelta_list
