# Reading Sessions

Api for book readers. Lets you keep time spent on each book

[Read me! Task notes](./documentation/task-notes.md)

Do `docker-compose up --build` for quick start or look [here](./documentation/setup.md) for some additional info

## Admin user

User admin adminpassword automatically created on start of a container. Use it for access to admin panel

## Endpoints

### /swagger/

We have swagger with all endpoints.

### /api/users/ and /api/users/{1}/ {user pk}

List and detail views for User model. List and details for each is available only for admin and stuff users. 
Owner can view his own profile

### /api/books/ and /api/books/{1}/ {book pk}

List and detail views for Book model

### /api/books/{1}/start/ and /api/books/{1}/start/ {book pk}

Starts(creates) reading session. Ends reading session. Only for authenticated. 
Users can Start reading session. If he tries to start again un-ended session with same book, nothing happens, start_time doesn't change.
Is User starts session with other book, old one closes. Book with start_time and no end_time is is_active.   

### /api/sessions/ and /api/sessions/{1}/ {sessions pk}

List and detail views for ReadingSession model

### /api/login/ /api/logout/ /api/signup/   

Login and signup endpoints. You can create new user and login with new credentials. 

## Docker

docker-compose file with main api service rs-api, nginx, redis, celery and worker for background tasks. 
On reach run 10 users and 10 books are created. Additionally, admin user admin:adminpassword. Task for 'daily_update_profiles' runs every minute
to faster simulate api work.

## Models

User - standard Django user model. 'username' and 'password' are used.

Book - book model with title, author, publication_year and description fields. 'book_total_reading_time' property returns time spent on book by all users

ReadingSession - unique_together for User and Book. Created one time for User-Book pair. Gets reopen when user returns to same book. Stores 'start_time', 'end_time'
for last activation, or no 'end_time' if user currently reading this book. Has a ton of methods and properties. Starts and Ends reading, handles total reading info.

ReadingProfile - OneToOne with User. Stores last 31 days (updates) of reading statistics. Has 'reading_last_week' and 'reading_last_month' info
