from datetime import timedelta, datetime
import sys
import urllib

from celery.schedules import crontab
from celery.task import periodic_task, task
from django.shortcuts import get_object_or_404
from django.utils.timezone import utc
import feedparser
from celery.exceptions import SoftTimeLimitExceeded, TimeLimitExceeded, WorkerShutdown
import redis

from articles.function import createArticleByUrl
from articles.models import Article

#read RSS feed every 15mins
#@periodic_task(run_every=crontab(minute='59,14,29,44'), time_limit=14 * 60, soft_time_limit=14 * 50 - 5, expires=60)
@periodic_task(run_every=timedelta(minutes=30), expires=60)
def scrapAll():
    lock_id = "scrapAll"
    have_lock = False
    my_lock = redis.Redis().lock(lock_id, timeout=30 * 60)
    try:
        have_lock = my_lock.acquire(blocking=False)
        if have_lock:
            print(lock_id + " lock acquired!")
            #scrapRSSFeed('feed://feeds.bbci.co.uk/news/rss.xml')
            #scrapRSSFeed('feed://feeds.bbci.co.uk/news/world/rss.xml')
            # scrapRSSFeed('feed://feeds.bbci.co.uk/news/uk/rss.xml')
            # scrapRSSFeed('feed://feeds.bbci.co.uk/news/world/europe/rss.xml')

            # scrapRSSFeed('feed://feeds.bbci.co.uk/news/business/rss.xml')
            # scrapRSSFeed('feed://feeds.bbci.co.uk/news/politics/rss.xml')
            # scrapRSSFeed('feed://feeds.bbci.co.uk/news/health/rss.xml')
            # scrapRSSFeed('feed://feeds.bbci.co.uk/news/education/rss.xml')
            # scrapRSSFeed('feed://feeds.bbci.co.uk/news/science_and_environment/rss.xml')
            # scrapRSSFeed('feed://feeds.bbci.co.uk/news/technology/rss.xml')
            # scrapRSSFeed('feed://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml')

            scrapRSSFeed('http://www.irishtimes.com/cmlink/news-1.1319192')
            # scrapRSSFeed('http://www.irishtimes.com/cmlink/business-1.1319195')
            # scrapRSSFeed('http://www.irishtimes.com/cmlink/sport-1.1319194')

        else:
            print(lock_id + " is locked by another worker!")
    except SoftTimeLimitExceeded:
        print('scrapAll soft time limit exceeded!')

    except (TimeLimitExceeded, WorkerShutdown):
        print('scrapAll hard time limit exceeded!')

    # except:
    #     print("Unexpected error:", sys.exc_info()[0])

    finally:
        if have_lock:
            print(lock_id + " released!")
            my_lock.release()


def scrapRSSFeed(feed):
    d = feedparser.parse(feed)

    for item in d['entries']:

        if "bbc" in item['link']:
            url = item['id']
            # url = url.replace(".co.uk/", ".com/")
        else:
            url = item['link']

        if '?localLinksEnabled=false' in url:
            url = url.replace('?localLinksEnabled=false', '')

        if '?feedType=RSS&feedName=topNews' in url:
            url = url.replace('?feedType=RSS&feedName=topNews', '')

        url = urllib.parse.quote(url, '/:')

        try:
            get_object_or_404(Article, url=url)
        except:
            try:
                article = createArticleByUrl(url)
                article.save()

            except Exception as err:
                print(err)
                print("Failed adding article " + url)
                pass
            else:
                print("Add New Article:" + article.Headline)

    print(feed + " Done!")