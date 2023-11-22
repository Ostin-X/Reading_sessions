import pytest
from django.contrib.auth.models import User
from books.models import ReadingProfile, ReadingSession
from unittest.mock import patch

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

        # with patch('books.models.ReadingSession.get_user_all_books_total_reading_time',
        #            return_value=timedelta(hours=3)):
        #     assert ReadingSession.get_user_all_books_total_reading_time(user) == timedelta(hours=3)
        #     reading_profile.update_daily_reading_profile()
        #
        #     assert reading_profile.reading_last_week == timedelta(seconds=10800)
        #     assert reading_profile.reading_last_month == timedelta(hours=3)
        #     assert reading_profile.last_day_total_reading_time == timedelta(hours=3)
        #     assert reading_profile.daily_reading_time == [timedelta(hours=3)]

        i_history = []

        with patch('books.models.ReadingSession.get_user_all_books_total_reading_time',
                   side_effect=[timedelta(seconds=n) for n in range(1, 11)]):
            for i in range(1, 11):
                # i_history.append(i)
                # assert i_history == [1] or [1, 2]
                # i2_history_7_days = sum(i_history)
                # if i_history == [1, 2, 3]:
                #     assert sum(i_history) == 6
                #     assert i2_history_7_days == 6
                i_history_7_days = sum(i_history[-2:])
                # assert ReadingSession.get_user_all_books_total_reading_time(user) == timedelta(seconds=i_history_7_days)
                assert timedelta(seconds=i_history_7_days) == ReadingSession.get_user_all_books_total_reading_time(user)

                reading_profile.update_daily_reading_profile()
                # assert i_history_7_days == 1
                # assert reading_profile.reading_last_week == timedelta(hours=i_history_7_days)
                # assert reading_profile.reading_last_month == timedelta(hours=3)
                # assert reading_profile.last_day_total_reading_time == timedelta(hours=3)
                # assert reading_profile.daily_reading_time == [timedelta(hours=3)]
