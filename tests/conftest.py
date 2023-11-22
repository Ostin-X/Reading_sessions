import pytest

from books.models import User, Book


def get_description(i):
    return 'i' * 100


@pytest.fixture
def user():
    return User.objects.create(username='testuser')


@pytest.fixture
def five_user():
    return [User.objects.create(username=f'testuser{i}') for i in range(1, 6)]


@pytest.fixture
def book():
    description = get_description(1)
    return Book.objects.create(title='Test Book', author='Test Author', publication_year=1981, description=description)


@pytest.fixture
def five_books():
    return [Book.objects.create(title=f'testtitle{i}', author=f'testauthor{i}', publication_year=1981,
                                description=get_description(i)) for i in range(1, 6)]
