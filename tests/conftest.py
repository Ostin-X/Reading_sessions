import pytest
from faker import Faker
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from books.models import User, Book


@pytest.fixture
def auto_login_user(api_client, user, test_password='1234567890'):
    def make_auto_login():
        url = reverse("rest_framework:login")
        data = {"username": user.username, "password": test_password}
        response = api_client.post(url, data=data)
        assert response.status_code == 200
        return api_client, user

    return make_auto_login


@pytest.fixture
def api_client():
    return APIClient()


def get_description(i):
    return 'i' * 100


@pytest.fixture
def user():
    return User.objects.create(username='testuser', password='password123')


@pytest.fixture
def five_users():
    return [User.objects.create(username=f'testuser{i}') for i in range(1, 6)]


@pytest.fixture
def book():
    description = get_description(1)
    return Book.objects.create(title='Test Book', author='Test Author', publication_year=1981, description=description)


@pytest.fixture
def five_books():
    return [Book.objects.create(title=f'testtitle{i}', author=f'testauthor{i}', publication_year=1981,
                                description=get_description(i)) for i in range(1, 6)]


@pytest.fixture
def fill_books():
    def create_books(number: int = 10):
        fake = Faker()
        created_books = 0
        for _ in range(number):
            book = Book.objects.create(title=fake.sentence(), author=fake.name(), publication_year=fake.year(),
                                       description=fake.text())
            created_books += 1
        return created_books

    return create_books
