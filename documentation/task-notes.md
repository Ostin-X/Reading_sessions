# Some notes and explanations

## DB design
I use one session for User-Book pair. It opens again, when user gets back to same book after end old reading session.
I guess it's not the best way, if we need to get a lot of different statistics. Well, like last 7 or 30 days.
I've added ReadingProfile model, that keeps total data for 31 days(or 31 updates actually). I ran myself into corner
with this design and no time to make it better.

## DB better design(maybe)
I would use one ReadingSession object for each session. If user would got back to same book, new session would be created.
And then use something like to get one week reading time. Well this and some more, to get sessions with part of time in last week 

`a_week_ago = now - timedelta(weeks=1)`

`user_sessions_last_week = ReadingSession.objects.filter(user=user, start_time__gte=a_week_ago)`

## ReadingSession methods and properties
I might've crated a God Class. Not shore, but looks not ok

## Testing
Well, it's not the best. It kinda did its job - I found some bugs. But it definitely needs to be better structured
and have separate test cases. More fixtures. It takes a bit of time, and I'm trying to get it done faster

## CRUD in Views and Serializers
Got carried away a bit with serializers. I guess it's better to refactor most of the operations to separate views
for better visibility. But I know what list(), get() put() in views are

## Docstrings
Well, they are not everywhere. Time, just needs more time. Sorry

### So dont be too harsh, please)
