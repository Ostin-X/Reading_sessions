from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import redirect
from django.urls import reverse
from .models import Book, ReadingSession, User
from rest_framework import viewsets, filters

from .permissions import OwnOrStuffPermission, ReadOnlyOrStuffPermission
from .serializers import ReadingSessionSerializer, UserSerializer, BookSerializer
from .utils import get_book_and_user


class UserModelViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [OwnOrStuffPermission]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ('username', 'email')
    ordering_fields = ('username', 'email')


class BookModelViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [ReadOnlyOrStuffPermission]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ('title', 'author', 'publication_year')
    ordering_fields = ('title', 'author', 'publication_year')


class ReadingSessionModelViewSet(viewsets.ModelViewSet):
    queryset = ReadingSession.objects.all()
    serializer_class = ReadingSessionSerializer
    permission_classes = [ReadOnlyOrStuffPermission]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ('user__username', 'book__title')
    ordering_fields = ('user__username', 'book__title')


class StartReading(APIView):
    """
    A view for starting a reading session.
    """

    def post(self, request, *args, **kwargs):
        user, book = get_book_and_user(kwargs, request)
        if user is None or book is None:
            return Response({"error": "User or Book not found."},
                            status=status.HTTP_404_NOT_FOUND)

        session, created = ReadingSession.objects.get_or_create(user=user, book=book)

        session.start_reading()

        serializer = ReadingSessionSerializer(session)
        return Response(serializer.data, status=status.HTTP_200_OK)


class EndReading(APIView):
    """
    A view for ending a reading session.
    """

    def post(self, request, *args, **kwargs):
        user, book = get_book_and_user(kwargs, request)

        if user is None or book is None:
            return Response({"error": "User or Book not found."},
                            status=status.HTTP_404_NOT_FOUND)

        try:
            session = ReadingSession.objects.get(user=user, book=book)
            session.end_reading()
            serializer = ReadingSessionSerializer(session)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ReadingSession.DoesNotExist:
            return Response({"error": "ReadingSession not found."}, status=status.HTTP_404_NOT_FOUND)


class RedirectToUserDetailView(APIView):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse('users-detail', kwargs={'pk': request.user.pk}))
        else:
            return Response({'detail': 'User is not authenticated'}, status=status.HTTP_400_BAD_REQUEST)
