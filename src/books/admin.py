from django.contrib import admin

from .models import Book, ReadingSession

admin.site.register(Book)
admin.site.register(ReadingSession)
