from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views
from .views import StartReading, EndReading, RedirectToUserDetailView

router = DefaultRouter()
router.register(r'users', views.UserModelViewSet, basename='users')
router.register(r'books', views.BookModelViewSet, basename='books')
router.register(r'sessions', views.ReadingSessionModelViewSet, basename='sessions')

urlpatterns = [
    path('', include(router.urls)),

    path('books/<int:book_id>/start/', StartReading.as_view(), name='start-reading'),
    path('books/<int:book_id>/end/', EndReading.as_view(), name='end-reading'),
    path('redirect-to-user-detail/', RedirectToUserDetailView.as_view(), name='redirect-to-user-detail'),

]
