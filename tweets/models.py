from django.db import models

# Create your models here.

class Tweet(models.Model):
    TweetID = models.CharField(max_length=100, unique=True)
    User = models.CharField(max_length=50)
    TweetContent = models.CharField(max_length=200)
    TweetContent_Clean = models.CharField(max_length=200, blank=True, null=True)
    DateTime = models.DateTimeField(db_index=True)
    Urls = models.URLField(max_length=200)
    Mentions = models.CharField(max_length=200)
    Hashtags = models.CharField(max_length=200)
    Image = models.CharField(max_length=200)
    Follower = models.IntegerField(default=0)
    Handled = models.BooleanField(db_index=True, default=False)

    def getUrls(self):
        if len(self.Urls) > 0:
            return self.Urls.split(';')
        else:
            return []

    def getMentions(self):
        if len(self.Mentions) > 0:
            return self.Mentions.split(';')
        else:
            return []

    def getHashtags(self):
        if len(self.Hashtags) > 0:
            return self.Hashtags.split(';')
        else:
            return []

    def getImage(self):
        if len(self.Image) > 0:
            return self.Image.split(';')
        else:
            return []
