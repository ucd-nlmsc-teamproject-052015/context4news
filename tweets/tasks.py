from datetime import timedelta, datetime

from celery.task import periodic_task, task
from django.utils.timezone import utc

from tweets.function import twitter_stream, listAuth, pollKeywords
from tweets.models import Tweet

@periodic_task(run_every=timedelta(minutes=4), expires=10)
def start_stream():
    keywordChunks = pollKeywords(limit=400, keyword_per_article=5, hours=24)

    print(keywordChunks)
    print("Start " + str(len(keywordChunks)) + " streaming connections!")
    for i in range(min(3, len(keywordChunks))):
        twitter_stream.apply_async((listAuth(i), keywordChunks[i], i + 1), expires=10)






