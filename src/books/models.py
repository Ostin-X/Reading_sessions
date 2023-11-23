import logging
from datetime import timedelta, datetime

import pytz
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import transaction, models


def get_empty_list():
    return []


def get_current_time_in_timezone(timezone='Europe/Kiev'):
    """
    Return the current time in the specified timezone.

    :param timezone: The timezone we want to use, default is 'Europe/Kiev'.
    :return: A datetime object of the current time in the specified timezone.
    """
    return datetime.now(pytz.timezone(timezone))


class ReadingProfile(models.Model):
    """Model for storing reading information of a User."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    reading_last_week = models.DurationField(default=timedelta(0))
    reading_last_month = models.DurationField(default=timedelta(0))
    last_day_total_reading_time = models.DurationField(default=timedelta(0))
    daily_reading_time = ArrayField(models.DurationField(), default=get_empty_list)

    def __str__(self):
        return f"{self.user.username}'s ReadingProfile"

    def _update_last_day_total_reading_time(self) -> timedelta:
        """
        Calculate the total reading time for the user for the last day and updates it in the profile.
        Returns the calculated reading time for the day.
        """
        current_total_reading_time = ReadingSession.get_user_all_books_total_reading_time(self.user)
        today_reading_time = current_total_reading_time - self.last_day_total_reading_time
        self.last_day_total_reading_time = current_total_reading_time
        return today_reading_time

    def _update_daily_reading_history(self):
        """
        Update the daily reading history for the user keeping records for the last 31 days.
        """
        if len(self.daily_reading_time) > 30:
            self.daily_reading_time = self.daily_reading_time[-30:]
        today_reading_time = self._update_last_day_total_reading_time()
        self.daily_reading_time.append(today_reading_time)

    def _update_reading_last_days(self, num_days: int) -> timedelta:
        """
        Calculate the total reading time for the user for the specified number of days,
        and return the total reading time for these days.

        :param num_days: The number of past days to consider.
        :return: The total reading time for the last num_days days.
        """
        num_days = min(num_days, len(self.daily_reading_time))
        if num_days < 1:
            return timedelta(0)

        total_reading_time_for_last_days = sum(self.daily_reading_time[-num_days:], timedelta())

        return total_reading_time_for_last_days

    @transaction.atomic
    def update_daily_reading_profile(self):
        """
        Update the reading profile for the user which includes the last week, last month reading times and history.
        """
        self._update_daily_reading_history()
        self.reading_last_week = self._update_reading_last_days(7)
        self.reading_last_month = self._update_reading_last_days(30)
        self.save()

    @classmethod
    def update_all_profiles(cls):
        """
        Class method to update the reading profiles for all users.
        """
        for profile in cls.objects.all():
            try:
                profile.update_daily_reading_profile()
            except Exception as e:
                logging.error(f"Error updating profile for user {profile.user.username}: {type(e).__name__}, {e}")


class Book(models.Model):
    """
    The Book model represents a book in the system with its title,
    author, publication year and a description.
    """
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    publication_year = models.IntegerField(validators=[MinValueValidator(1450), MaxValueValidator(datetime.now().year)])
    description = models.TextField()

    def __str__(self):
        return f'{self.title} by {self.author} ({self.publication_year})'

    @property
    def book_total_reading_time(self):
        """
        Calculates and returns the total reading time spent on the book.
        If an error occurs during the calculation, logs the error and returns a timedelta of zero.
        """
        try:
            sessions = self.readingsession_set.all()
            total_reading_time = sum((session.session_total_reading_time for session in sessions), timedelta())
            return total_reading_time
        except Exception as e:
            logging.error(f"Error calculating total reading time for book {self.id}: {type(e).__name__}, {e}")
            return timedelta(0)


class ReadingSession(models.Model):
    """
    A ReadingSession represents a period of time that a user has spent reading a book. Each session is related to a User
    and a Book. Each session stores the start and end time, and the total time of that session. A User cannot change the
    'User' and 'Book' of an existing reading session.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    total_time = models.DurationField(default=timedelta(0))

    def __init__(self, *args, **kwargs):
        """
        Initialize ReadingSession and store original user and book id's to prevent changes.
        """
        super().__init__(*args, **kwargs)
        self.__original_user = self.user_id
        self.__original_book = self.book_id

    def __str__(self):
        return f'{self.user.username} - {self.book.title}'

    def clean(self):
        """
        Ensures that the user and book of an existing reading session cannot be changed.
        """
        if self.pk and (self.user_id != self.__original_user or self.book_id != self.__original_book):
            raise ValidationError("Cannot change the 'user' and 'book' of an existing reading session.")

    def save(self, *args, **kwargs):
        """
        Saves the ReadingSession instance, while also performing a full clean (all field and model validations).
        """
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def is_active(self):
        """
        Evaluates whether the reading session is currently active.
        """
        return self.start_time and self.end_time is None

    @property
    def session_total_reading_time(self):
        """
        Calculates and returns the total reading time of the session including new time of active sesison.
        """
        total_time = self.total_time if (self.end_time or not self.start_time) else self.total_time + (
                get_current_time_in_timezone() - self.start_time)
        return total_time

    def start_reading(self):
        """
            Starts a reading session for a user.
            Sends request to end all other sessions for the same user that are currently active.
        """
        try:
            with transaction.atomic():
                open_sessions = ReadingSession.objects.select_for_update().exclude(id=self.id).filter(user=self.user,
                                                                                                      end_time__isnull=True)
                for session in open_sessions:
                    session.end_reading()

        except transaction.TransactionManagementError:
            # Safely ignore the transaction error.
            pass
        try:
            if self.start_time is None or self.start_time and self.end_time:
                self.start_time = get_current_time_in_timezone()
                self.end_time = None
                self.save()
        except Exception as e:
            logging.error("Error occurred when starting a reading session: %s", e)

    def end_reading(self):
        """
            Ends a current reading session.
        """
        try:
            if self.start_time and not self.end_time:
                self.end_time = get_current_time_in_timezone()
                self.total_time += self.end_time - self.start_time
                self.save()
        except Exception as e:
            logging.error("Error occurred when ending a reading session: %s", e)

    @classmethod
    def get_user_all_books_total_reading_time(cls, user):
        """
        Calculate the total time a user has spent reading all their books.

        This method returns the sum of session_total_reading_time for all reading sessions
        associated with the given user. session_total_reading_time is a property of the
        ReadingSession model, which returns the total time spent in a reading session,
        including any ongoing session time.

        :param user: User object for whom to sum up all reading time.
        :return: Returns total reading time as a timedelta object.
        """
        return sum((session.session_total_reading_time for session in cls.objects.filter(user=user)), timedelta())

    class Meta:
        unique_together = ('user', 'book')
