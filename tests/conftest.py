import pytest
from faker import Faker
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from books.models import User, Book


@pytest.fixture
def api_client():
    return APIClient()


def get_description(i):
    return 'i' * 100


@pytest.fixture
def user():
    return User.objects.create(username='testuser', password='password123')


@pytest.fixture
def fill_users():
    def create_users(number: int = 10):
        fake = Faker()
        created_users = 0
        for _ in range(number):
            fake_name = fake.name()
            while fake_name in User.objects.values_list('username', flat=True):
                fake_name = fake.name()
            user = User.objects.create(username=fake_name)
            created_users += 1
        return created_users

    return create_users


@pytest.fixture
def book():
    description = get_description(1)
    return Book.objects.create(title='Test Book', author='Test Author', publication_year=1981, description=description)


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
