from celery import shared_task
from datetime import timedelta


def default_schedule(minutes=1):
    return timedelta(minutes=minutes)


@shared_task
def daily_update_profiles():
    from books.models import ReadingProfile
    ReadingProfile.update_all_profiles()

    print('_____________________________________________')
    print('_____________________________________________')
    print('WORKER HERE')
    print('_____________________________________________')
    print('_____________________________________________')
    return 'WORKER HERE'
