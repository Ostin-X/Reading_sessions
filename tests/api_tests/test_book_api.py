from datetime import timedelta

import pytest
from django.urls import reverse

from books.models import ReadingSession


@pytest.mark.django_db
class TestBookAPI:

    @pytest.fixture(autouse=True)
    def setup_class(self, api_client, book, fill_books, user):
        self.api_client = api_client
        self.test_book = book
        self.books = fill_books(100)
        self.test_user = user

    def test_books_list(self):
        url = reverse('books-list')

        response = self.api_client.get(url)

        assert response.status_code == 200
        assert len(response.data) == 101
        assert response.data[0]['title'] == self.test_book.title
        assert response.data[0]['author'] == self.test_book.author
        assert response.data[0]['publication_year'] == self.test_book.publication_year
        assert response.data[0]['short_description'] == self.test_book.description[:50] + '...'
        assert 'description' not in response.data[0]

    @pytest.mark.parametrize('logged', (False, True))
    def test_books_detail(self, logged):
        url = reverse('books-detail', kwargs={'pk': self.test_book.id})

        if logged:
            self.api_client.force_authenticate(user=self.test_user)

        response = self.api_client.get(url)

        assert response.status_code == 200
        assert response.data['title'] == self.test_book.title
        assert response.data['author'] == self.test_book.author
        assert response.data['publication_year'] == self.test_book.publication_year
        assert response.data['short_description'] == self.test_book.description[:50] + '...'
        assert response.data['description'] == self.test_book.description
        assert response.data['book_total_reading_time'] == timedelta(0)

        if logged:
            assert response.data['last_reading_session'] is None
            assert response.data['user_book_total_reading_time'] == 0
        else:
            assert 'last_reading_session' not in response.data
            assert 'user_book_total_reading_time' not in response.data

    def test_book_start_reading(self):
        assert ReadingSession.objects.count() == 0

        url = reverse('start-reading', kwargs={'pk': self.test_book.id})
        self.api_client.force_authenticate(user=self.test_user)

        response = self.api_client.post(url)

        # assert response.data == 4
        assert response.status_code == 200
        assert len(response.data) == 6
        assert response.data['id'] == ReadingSession.objects.first().id
        assert response.data['start_time']
        assert response.data['end_time'] is None
        assert response.data['user'] == self.test_user.id
        assert response.data['book'] == self.test_book.id

        assert ReadingSession.objects.count() == 1
        assert ReadingSession.objects.first().book == self.test_book
        assert ReadingSession.objects.first().user == self.test_user
