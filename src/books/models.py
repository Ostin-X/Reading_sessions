from datetime import timedelta, datetime

import pytz
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models


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
        total_reading_time = sum(session.session_total_reading_time.total_seconds() for session in sessions)
        return total_reading_time


class ReadingSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    total_time = models.DurationField(default=timedelta(0))

    class Meta:
        unique_together = ('user', 'book')

    def __str__(self):
        return f'{self.user.username} - {self.book.title}'

    def start_reading(self):
        open_session = ReadingSession.objects.exclude(id=self.id).filter(user=self.user, end_time__isnull=True).first()
        if open_session:
            open_session.end_reading()

        if self.start_time is None or self.start_time and self.end_time:
            self.start_time = datetime.now(pytz.timezone('Europe/Kiev'))
            self.end_time = None
            self.save()

    def end_reading(self):
        if self.start_time and not self.end_time:
            self.end_time = datetime.now(pytz.timezone('Europe/Kiev'))

            self.total_time += self.end_time - self.start_time
            self.save()

    @property
    def is_active(self):
        return self.end_time is None

    @property
    def session_total_reading_time(self):
        total_time = self.total_time if self.end_time else self.total_time + (
                datetime.now(pytz.timezone('Europe/Kiev')) - self.start_time)
        return total_time

    @classmethod
    def get_user_all_books_total_reading_time(cls, user):
        return sum((session.session_total_reading_time for session in cls.objects.filter(user=user)), timedelta())

    def clean(self):
        # if not self._state.adding and (self.user_id != self.__original_user or self.book_id != self.__original_book):
        if self.pk and (self.user_id != self.__original_user or self.book_id != self.__original_book):
            raise ValidationError("Cannot change the 'user' and 'book' of an existing reading session.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_user = self.user_id
        self.__original_book = self.book_id
