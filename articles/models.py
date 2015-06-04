import datetime

from django.db import models
from django.utils import timezone

# Create your models here.
class Article(models.Model):
    Headline = models.CharField(max_length=500, blank=True)
    SubHeadline = models.CharField(max_length=1000, blank=True)
    Url = models.URLField(max_length=400, unique=True, blank=True, null=True)
    DateTime = models.DateTimeField('date published', db_index=True)
    Keywords = models.CharField(max_length=5000)
    Content = models.TextField(blank=True)
    Type = models.CharField(max_length=100, db_index=True)
    Source = models.CharField(max_length=100)

    def was_published_recently(self):
        return self.DateTime >= timezone.now() - datetime.timedelta(days=1)

    def splitContent(self):
        return self.Content.split('\n')

    def getKeywords(self):
        return self.Keywords.split(",")

    def getSourceHeadline(self):
        return self.Source + ": " + self.Headline

