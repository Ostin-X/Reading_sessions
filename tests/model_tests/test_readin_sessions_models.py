from datetime import timedelta

import pytest
from django.core.exceptions import ValidationError
from django.db.models import Sum

from books.models import Book, User, ReadingSession


@pytest.mark.django_db(transaction=True)
class TestReadingSessionModel:

    def test_start_start_end_session_flow(self, user, five_books):
        assert Book.objects.count() == 5
        assert User.objects.count() == 1
        assert ReadingSession.objects.count() == 0

        book1 = five_books[0]
        book2 = five_books[1]
        book3 = five_books[2]

        # Creating session, not starting.
        reading_session1 = ReadingSession.objects.create(user=user, book=book1)

        assert ReadingSession.objects.count() == 1
        assert not reading_session1.is_active
        assert not reading_session1.start_time and not reading_session1.end_time

        # Starting session 1.
        reading_session1.start_reading()

        assert ReadingSession.objects.count() == 1
        assert reading_session1.start_time and not reading_session1.end_time
        assert reading_session1.is_active

        # Creating session 2, not starting. Updating session 1 info.
        reading_session2 = ReadingSession.objects.create(user=user, book=book2)
        reading_session1 = ReadingSession.objects.get(pk=reading_session1.pk)

        assert ReadingSession.objects.count() == 2
        assert reading_session1.is_active
        assert not reading_session2.is_active
        assert reading_session1.start_time and not reading_session1.end_time
        assert not reading_session2.start_time and not reading_session2.end_time

        # Starting session 2. Updating session 1 info.
        reading_session2.start_reading()
        reading_session1 = ReadingSession.objects.get(pk=reading_session1.pk)

        assert ReadingSession.objects.count() == 2
        assert not reading_session1.is_active
        assert reading_session2.is_active
        assert reading_session1.start_time and reading_session1.end_time
        assert reading_session2.start_time and not reading_session2.end_time

        # Ending session 2. Updating session 1 info.
        reading_session2.end_reading()
        reading_session1 = ReadingSession.objects.get(pk=reading_session1.pk)

        assert ReadingSession.objects.count() == 2
        assert not reading_session1.is_active
        assert not reading_session2.is_active
        assert reading_session1.start_time and reading_session1.end_time
        assert reading_session2.start_time and reading_session2.end_time

        # Starting session 1 again. Updating session 2 info.
        reading_session1.start_reading()
        reading_session2 = ReadingSession.objects.get(pk=reading_session2.pk)

        assert ReadingSession.objects.count() == 2
        assert reading_session1.is_active
        assert not reading_session2.is_active
        assert reading_session1.start_time and not reading_session1.end_time
        assert reading_session2.start_time and reading_session2.end_time

        # Ending session 2, not active. Updating both sessions info. Nothing should change.
        reading_session2.end_reading()
        reading_session1 = ReadingSession.objects.get(pk=reading_session1.pk)
        reading_session2 = ReadingSession.objects.get(pk=reading_session2.pk)

        assert ReadingSession.objects.count() == 2
        assert reading_session1.is_active
        assert not reading_session2.is_active
        assert reading_session1.start_time and not reading_session1.end_time
        assert reading_session2.start_time and reading_session2.end_time

        # Starting session 1 again. Start time should remain.
        old_start_time = reading_session1.start_time
        reading_session1.start_reading()
        reading_session1 = ReadingSession.objects.get(pk=reading_session1.pk)
        new_start_time = reading_session1.start_time

        assert ReadingSession.objects.count() == 2
        assert reading_session1.start_time and not reading_session1.end_time
        assert reading_session1.is_active
        assert old_start_time == new_start_time

        # Forcing session 2 in is_active. Unnatural condition. Creating and starting session 3.
        reading_session2.end_time = None
        reading_session2.save()
        reading_session1 = ReadingSession.objects.get(pk=reading_session1.pk)
        reading_session2 = ReadingSession.objects.get(pk=reading_session2.pk)

        assert reading_session1.is_active
        assert reading_session2.is_active

        reading_session3 = ReadingSession.objects.create(user=user, book=book3)
        reading_session3.start_reading()
        reading_session1 = ReadingSession.objects.get(pk=reading_session1.pk)
        reading_session2 = ReadingSession.objects.get(pk=reading_session2.pk)

        assert ReadingSession.objects.count() == 3
        assert not reading_session1.is_active
        assert not reading_session2.is_active
        assert reading_session3.is_active
        assert reading_session1.start_time and reading_session1.end_time
        assert reading_session2.start_time and reading_session2.end_time
        assert reading_session3.start_time and not reading_session3.end_time

        # get_user_all_books_total_reading_time test
        microsecond_diff = timedelta(microseconds=1000)
        get_user_all_books_total_reading_time = ReadingSession.get_user_all_books_total_reading_time(user)
        test_value = timedelta()
        for session in ReadingSession.objects.all():
            test_value += session.session_total_reading_time
        assert abs(get_user_all_books_total_reading_time - test_value) <= microsecond_diff

        reading_session3.end_reading()
        get_user_all_books_total_reading_time = ReadingSession.get_user_all_books_total_reading_time(user)
        test_value = ReadingSession.objects.filter(user=user).aggregate(total_time=Sum('total_time'))

        assert get_user_all_books_total_reading_time == test_value['total_time']

    def test_user_book_change_time(self, five_user, five_books):
        assert Book.objects.count() == 5
        assert User.objects.count() == 5

        user1 = five_user[0]
        user2 = five_user[1]
        book1 = five_books[0]
        book2 = five_books[1]

        reading_session = ReadingSession.objects.create(user=user1, book=book1, )

        assert ReadingSession.objects.count() == 1

        try:
            print(reading_session.user)
            reading_session.user = user2
            reading_session.save()
            print(reading_session.user)
        except Exception as e:
            assert type(e) == ValidationError
            assert e.messages[0] == "Cannot change the 'user' and 'book' of an existing reading session."
        else:
            assert False
