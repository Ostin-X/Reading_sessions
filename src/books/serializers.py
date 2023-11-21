from django.db.models import F
from rest_framework import serializers

from .models import Book, ReadingSession, User, ReadingProfile


class UserReadingSessionSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(read_only=True)

    # book = serializers.StringRelatedField()
    # formatted_total_reading_time = serializers.SerializerMethodField()

    class Meta:
        model = ReadingSession
        fields = ('book', 'session_total_reading_time', 'is_active')
        # fields = ('start_time', 'end_time', 'book', 'total_reading_time', 'is_active')
        # fields = ('book', 'formatted_total_reading_time', 'is_active')

    # def get_formatted_total_reading_time(self, obj):
    #     total_time = obj.total_reading_time
    #
    #     if total_time:
    #         hours, remainder = divmod(total_time.total_seconds(), 3600)
    #         minutes, seconds = divmod(remainder, 60)
    #         return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    #     return None


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    sessions = serializers.SerializerMethodField()
    reading_last_week = serializers.SerializerMethodField()
    reading_last_month = serializers.SerializerMethodField()
    user_all_books_total_reading_time = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'username', 'password', 'reading_last_week', 'reading_last_month',
            'user_all_books_total_reading_time',
            'sessions')

    def get_sessions(self, obj):
        sessions = obj.readingsession_set.order_by(F('end_time').desc(nulls_first=True))
        return UserReadingSessionSerializer(sessions, many=True).data

    def get_user_all_books_total_reading_time(self, obj):
        return ReadingSession.get_user_all_books_total_reading_time(obj)
        # total_time = ReadingSession.get_user_total_reading_time(obj)
        # hours, remainder = divmod(total_time.total_seconds(), 3600)
        # minutes, seconds = divmod(remainder, 60)
        # return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

    def get_reading_last_week(self, obj):
        return obj.readingprofile.reading_last_week.total_seconds()

    def get_reading_last_month(self, obj):
        return obj.readingprofile.reading_last_month.total_seconds()


class BookSerializer(serializers.ModelSerializer):
    short_description = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = ('id', 'title', 'author', 'publication_year', 'short_description', 'description')

    def get_short_description(self, obj):
        # from books.tasks import get_print
        # get_print.delay()
        return obj.description[:50] + '...'

    def get_last_reading_session(self, obj):
        request = self.context.get("request")
        user = request.user if request else None

        sessions = ReadingSession.objects.filter(book=obj, user=user).order_by('-end_time')

        if not sessions:
            return None

        latest_session = sessions[0]

        if latest_session.is_active:
            return 'is_active'
        if time := latest_session.end_time:
            return time

    def get_user_book_total_reading_time(self, instance, user):
        reading_session = ReadingSession.objects.filter(book=instance, user=user).first()
        return reading_session.session_total_reading_time.total_seconds() if reading_session else 0

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get("request")

        if request and str(instance.id) in request.path.split("/"):
            if request.user.is_authenticated:
                representation['last_reading_session'] = self.get_last_reading_session(instance)
                representation['user_book_total_reading_time'] = self.get_user_book_total_reading_time(instance,
                                                                                                       request.user)
            representation['book_total_reading_time'] = instance.book_total_reading_time
        else:
            representation.pop('description')

        return representation


class ReadingSessionSerializer(serializers.ModelSerializer):
    total_time = serializers.CharField(read_only=True)
    start_time = serializers.DateTimeField(read_only=True)
    end_time = serializers.DateTimeField(read_only=True)

    # is active

    class Meta:
        model = ReadingSession
        fields = '__all__'
