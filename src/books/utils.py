from .models import Book, User


def get_book_and_user(kwargs, request):
    try:
        book_id = kwargs.get('book_id')
        user = request.user
        book = Book.objects.get(pk=book_id)
        return user, book
    except (User.DoesNotExist, Book.DoesNotExist):
        return None, None
