from datetime import timedelta, datetime
from django.contrib.postgres.fields import ArrayField

import pytz
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.dateparse import parse_duration


def get_empty_list():
    return []


def get_current_time_in_timezone(timezone='Europe/Kiev'):
    return datetime.now(pytz.timezone(timezone))


class ReadingProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    reading_last_week = models.DurationField(default=timedelta(0))
    reading_last_month = models.DurationField(default=timedelta(0))
    last_day_total_reading_time = models.DurationField(default=timedelta(0))
    # daily_reading_time = models.JSONField(default=get_empty_list)
    # daily_reading_time = ArrayField(models.TextField(), default=list)
    daily_reading_time = ArrayField(models.DurationField(), default=list)

    def __str__(self):
        return f"{self.user.username}'s ReadingProfile"

    def _update_last_day_total_reading_time(self) -> timedelta:
        """Calculate last day's total reading time and updates it."""
        current_total_reading_time = ReadingSession.get_user_all_books_total_reading_time(self.user)
        today_reading_time = current_total_reading_time - self.last_day_total_reading_time
        self.last_day_total_reading_time = current_total_reading_time
        return today_reading_time

    def _update_daily_reading_history(self):
        """Update the daily reading history for last 31 days"""
        if len(self.daily_reading_time) > 30:
            self.daily_reading_time = self.daily_reading_time[-30:]
        # today_reading_time = self._update_last_day_total_reading_time()
        today_reading_time = str(self._update_last_day_total_reading_time())
        self.daily_reading_time.append(today_reading_time)
        self.save()

    def _update_reading_last_days(self, num_days) -> timedelta:
        """Calculate the total reading time for the specified number of days."""
        num_days = min(num_days, len(self.daily_reading_time))
        if num_days < 1:
            return timedelta(0)

        reading_times = [parse_duration(time_str) for time_str in self.daily_reading_time[-num_days:]]
        total_reading_time = sum(reading_times, timedelta())

        return total_reading_time

    def update_daily_reading_profile(self):
        """Update the daily reading profile including last week, last month, and history."""
        self._update_daily_reading_history()
        self.reading_last_week = self._update_reading_last_days(7)
        self.reading_last_month = self._update_reading_last_days(30)
        self.save()

    @classmethod
    def update_all_profiles(cls):
        """Update the daily all reading profiles"""
        for profile in cls.objects.all():
            try:
                profile.update_daily_reading_profile()
            except Exception as e:
                print(f"Error updating profile for user {profile.user.username}: {e}")


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    publication_year = models.IntegerField()
    description = models.TextField()

    def __str__(self):
        return f'{self.title} by {self.author} ({self.publication_year})'

    @property
    def book_total_reading_time(self):
        sessions = self.readingsession_set.all()
        total_reading_time = sum((session.session_total_reading_time for session in sessions), timedelta())
        return total_reading_time


class ReadingSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    total_time = models.DurationField(default=timedelta(0))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_user = self.user_id
        self.__original_book = self.book_id

    def __str__(self):
        return f'{self.user.username} - {self.book.title}'

    def clean(self):
        # if not self._state.adding and (self.user_id != self.__original_user or self.book_id != self.__original_book):
        if self.pk and (self.user_id != self.__original_user or self.book_id != self.__original_book):
            raise ValidationError("Cannot change the 'user' and 'book' of an existing reading session.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def is_active(self):
        return self.end_time is None

    @property
    def session_total_reading_time(self):
        total_time = self.total_time if self.end_time else self.total_time + (
                get_current_time_in_timezone() - self.start_time)
        return total_time

    def start_reading(self):
        open_session = ReadingSession.objects.exclude(id=self.id).filter(user=self.user, end_time__isnull=True).first()
        if open_session:
            open_session.end_reading()

        if self.start_time is None or self.start_time and self.end_time:
            self.start_time = get_current_time_in_timezone()
            self.end_time = None
            self.save()

    def end_reading(self):
        if self.start_time and not self.end_time:
            self.end_time = get_current_time_in_timezone()

            self.total_time += self.end_time - self.start_time
            self.save()

    @classmethod
    def get_user_all_books_total_reading_time(cls, user):
        return sum((session.session_total_reading_time for session in cls.objects.filter(user=user)), timedelta())

    class Meta:
        unique_together = ('user', 'book')
