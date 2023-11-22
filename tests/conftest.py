import pytest

from books.models import ReadingProfile, User, Book


@pytest.fixture
def user():
    return User.objects.create(username='testuser')


# @pytest.fixture
# def five_user():
#     return [User.objects.create(username=f'testuser{i}') for i in range(1, 6)]


@pytest.fixture
def reading_profile(user):
    return ReadingProfile.objects.get(user=user)


@pytest.fixture
def book():
    description = '1' * 100
    return Book.objects.create(title='Test Book', author='Test Author', publication_year=1981, description=description)
