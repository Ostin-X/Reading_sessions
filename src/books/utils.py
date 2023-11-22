from .models import Book, User


def get_book_and_user(request, kwargs):
    try:
        book_id = kwargs.get('pk')
        user = request.user
        book = Book.objects.get(pk=book_id)
        return user, book
    except (User.DoesNotExist, Book.DoesNotExist):
        return None, None
