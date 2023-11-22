import pytest
from books.models import ReadingProfile, User


@pytest.fixture
def return_true():
    return True


@pytest.fixture
def return_false():
    return False


@pytest.fixture
def user():
    return User.objects.create(username='testuser')


@pytest.fixture
def reading_profile(user):
    return ReadingProfile.objects.get(user=user)
