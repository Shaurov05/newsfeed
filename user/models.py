from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Source(models.Model):
    source_id = models.CharField(max_length=40)
    source_name = models.CharField(max_length=250)

    def __str__(self):
        return self.source_name


class Country(models.Model):
    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    sources = models.ManyToManyField(Source, through="SourceChoice")
    countries = models.ManyToManyField(Country, through="CountryChoice")
    keywords = models.CharField(max_length=256, null=True, blank=True)
    chosen = models.BooleanField(default=False)
    user = models.OneToOneField(User,on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


class CountryChoice(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="user_countries")
    country = models.ForeignKey(Country, related_name="countries", on_delete=models.CASCADE)
    country_name = models.CharField(max_length=60)

    def __str__(self):
        return self.country.name


class SourceChoice(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="user_sources")
    source = models.ForeignKey(Source, related_name="sources", on_delete=models.CASCADE)
    source_name = models.CharField(max_length=60)

    def __str__(self):
        return self.source.source_name
