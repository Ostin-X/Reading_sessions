from django.contrib import admin
from django.urls import path, include

from .yasg import urlpatterns as doc_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('books.urls')),
    path('api/', include('rest_framework.urls')),
    # path('api/drf-auth/', include('rest_framework.urls')),
    *doc_urls,
]
