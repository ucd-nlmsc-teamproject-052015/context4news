from django.shortcuts import render

from tweets.models import Tweet
from django.http import HttpResponse
from django.utils.timezone import utc
from datetime import timedelta, datetime

# Create your views here.

def tweet_index(request):
    return HttpResponse("Hello, world. You're at the tweets index view.")


def tweet_list(request):
    #try:

        th = datetime.now().replace(tzinfo=utc) - timedelta(hours=24*7)
        list_of_tweets = Tweet.objects.filter(DateTime__gte=th).order_by('-DateTime')
        print(len(list_of_tweets))

        return render(request, 'tweet_list.html',
                      {'latest_tweets_list': list_of_tweets[:100], 'total': len(list_of_tweets)})
    #except:
    #    return render(request, 'tweet_list.html')