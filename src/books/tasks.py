from celery import shared_task


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
