from datetime import timedelta

import pytest
from django.urls import reverse

from books.models import ReadingSession, User


@pytest.mark.django_db
class TestBookAPI:

    @pytest.fixture(autouse=True)
    def setup_class(self, api_client, book, fill_books, user, fill_users):
        self.api_client = api_client
        self.test_book = book
        fill_books(100)
        self.test_user = user
        fill_users(100)

    @pytest.mark.parametrize('logged, stuff, response_code', [
        (False, False, 403),
        (True, False, 403),
        (True, True, 200),
    ], )
    def test_users_list(self, logged, stuff, response_code):
        url = reverse('users-list')

        if logged:
            if stuff:
                self.test_user.is_staff = True
                reading_session = ReadingSession.objects.create(user=self.test_user, book=self.test_book)
                reading_session.start_reading()
                reading_session.end_reading()
            self.api_client.force_authenticate(user=self.test_user)

        response = self.api_client.get(url)

        assert response.status_code == response_code
        assert len(response.data) == 100 * stuff + 1
        if stuff:
            assert response.data[0]['username'] == self.test_user.username
            assert response.data[0]['reading_last_week'] == self.test_user.readingprofile.reading_last_week
            assert response.data[0]['reading_last_month'] == self.test_user.readingprofile.reading_last_month
            assert response.data[0][
                       'user_all_books_total_reading_time'] == ReadingSession.get_user_all_books_total_reading_time(
                self.test_user)

            assert response.data[0]['sessions'][0]['book'] == self.test_book.id
            assert response.data[0]['sessions'][0][
                       'session_total_reading_time'] == self.test_user.readingsession_set.get(
                book=self.test_book).session_total_reading_time
            assert response.data[0]['sessions'][0]['is_active'] is False

    @pytest.mark.parametrize('logged, stuff, owner, response_code', [
        (False, False, False, 403),
        (True, False, False, 403),
        (True, False, True, 200),
        (True, True, False, 200),
    ], )
    def test_users_detail(self, logged, stuff, owner, response_code):
        url = reverse('users-detail', kwargs={'pk': self.test_user.id})
        other_user = User.objects.exclude(id=self.test_user.id).first()

        if logged and not owner and not stuff:
            self.api_client.force_authenticate(user=other_user)
        elif stuff:
            other_user.is_staff = True
            self.api_client.force_authenticate(user=other_user)
        elif logged and owner and not stuff:
            self.api_client.force_authenticate(user=self.test_user)

        reading_session = ReadingSession.objects.create(user=self.test_user, book=self.test_book)
        reading_session.start_reading()
        reading_session.end_reading()

        response = self.api_client.get(url)

        assert response.status_code == response_code
        assert len(response.data) == 5 * (stuff or owner) + 1

        if stuff or owner:
            assert response.data['username'] == self.test_user.username
            assert response.data['reading_last_week'] == self.test_user.readingprofile.reading_last_week
            assert response.data['reading_last_month'] == self.test_user.readingprofile.reading_last_month
            assert response.data[
                       'user_all_books_total_reading_time'] == ReadingSession.get_user_all_books_total_reading_time(
                self.test_user)

            assert response.data['sessions'][0]['book'] == self.test_book.id
            assert response.data['sessions'][0][
                       'session_total_reading_time'] == self.test_user.readingsession_set.get(
                book=self.test_book).session_total_reading_time
            assert response.data['sessions'][0]['is_active'] is False
