from django.db import models


class ScrapedData(models.Model):
    name = models.CharField(max_length=255)
    avatar = models.URLField()
    country_of_birth = models.CharField(max_length=100)
    place_of_birth = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    job = models.CharField(max_length=100)
    languages = models.CharField(max_length=255)
    political_party = models.CharField(max_length=255)
    email = models.EmailField()
    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
