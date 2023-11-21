from django.contrib import admin

from .models import Book, ReadingSession, ReadingProfile

admin.site.register(ReadingProfile)
admin.site.register(Book)
admin.site.register(ReadingSession)
