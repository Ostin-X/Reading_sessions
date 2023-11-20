from django.core.management import BaseCommand
from django.db import transaction
from faker import Faker

from books.models import Book

fake = Faker()


class Command(BaseCommand):
    help = 'Create some books'

    def add_arguments(self, parser):
        parser.add_argument('-c', '--count', type=int, help='Indicates the number of books to be created')

    def handle(self, *args, **kwargs):
        count = kwargs.get('count', 20)

        with transaction.atomic():
            for _ in range(count):
                Book.objects.create(
                    title=fake.sentence(nb_words=3),
                    author=fake.name(),
                    publication_year=fake.pyint(min_value=1900, max_value=2022),
                    description=fake.text(max_nb_chars=200),
                )
            self.stdout.write(self.style.SUCCESS('Books created successfully'))
            self.stdout.write(self.style.SUCCESS(f'Total books: {Book.objects.count()}'))
