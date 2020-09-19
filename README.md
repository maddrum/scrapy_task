Welcome to Bulgarian MP catalogue!
This webapp contains a web crawler and Django Rest Framework web API, installed in folders "crawler" and "django_scrapy_task", respectively.


In order to use this you should:
  1. Clone this repository somewhere in ~/
  2. Create a venv based on Python 3.8 and install all requirements from requirements.txt
  -------- From inside the django app folder(~/cloned-folder/django_scrapy_task)
  3. Migrate the database with "python manage.py migrate"
  4. Create a superuser for the Django Admin using "python manage.py createsuperuser".
  5. Start the django app with "python manage.py runserver".
    a. optional: Add users to /admin if needed.
  -------- 
  6. Crawl the information. Run "scrapy crawl mp" in ~/cloned-folder/crawler/scrapy_scraler/. This will populate the database. You may need to do this a several times due to the parliament.bg security
  7. Information is now available in /api
  8. Enjoy
  
