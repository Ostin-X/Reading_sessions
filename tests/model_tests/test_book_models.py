from datetime import timedelta
from unittest.mock import patch, Mock

import pytest

from books.models import Book


@pytest.mark.django_db(transaction=True)
class TestReadingProfileSignal:

    def test_book_total_reading_time(self, book):
        assert Book.objects.count() == 1

        mock_sessions = [Mock(session_total_reading_time=timedelta(seconds=i)) for i in range(1, 6)]

        with patch.object(Book, 'readingsession_set') as mock_readingsession_set:
            mock_readingsession_set.all.return_value = mock_sessions
            expected_reading_time = timedelta(seconds=15)

            assert book.book_total_reading_time == expected_reading_time
