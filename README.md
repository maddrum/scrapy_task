Welcome to Bulgarian MP catalogue!
This webapp contains a web crawler and Django Rest Framework web API, installed in folders "crawler" and "django_scrapy_task", respectively.


In order to use this you should:
  1. Clone this repository
  2. Create a venv based on Python 3.8 and install all requirements from requirements.txt
  3. Migrate the database with "python manage.py migrate"
  3. Create a superuser for the Django Admin using "python manage.py createsuperuser". Add normal users if needed from the Django Admin
  4. Crawl the information. Run "scrapy crawl mp" in ~/crawler/scrapy_scraler/ folder. This will populate the database. You may need to do this a several times due to the parliament.bg security
  5. Start the django app with "python manage.py runserver". 
  6. Information is now available in /api
  7. Enjoy
  
