from django.core.management import BaseCommand
from django.db import transaction
from faker import Faker

from books.models import User

fake = Faker()


class Command(BaseCommand):
    help = 'Create fake users'

    def add_arguments(self, parser):
        parser.add_argument('-c', '--count', type=int, help='Indicates the number of users to be created')

    def handle(self, *args, **kwargs):
        if not (count := kwargs['count']):
            count = 10

        with transaction.atomic():
            for _ in range(count):
                User.objects.create(
                    username=fake.name(),
                    password=fake.password(),
                )
            self.stdout.write(self.style.SUCCESS('Fake users created'))
            self.stdout.write(self.style.SUCCESS(f'Total users: {User.objects.count()}'))
