import re
from datetime import timedelta, datetime

import nltk
from twitter import OAuth, TwitterStream
from celery.task import task
from django.utils.timezone import utc
from celery.exceptions import SoftTimeLimitExceeded, TimeLimitExceeded, WorkerShutdown
import redis

from articles.models import Article
from tweets.models import Tweet

@task(time_limit=235, soft_time_limit=225, ignore_result=True)
def twitter_stream(Auth, search_term, number):
    lock_id = "twitter_stream_" + str(number)
    have_lock = False
    my_lock = redis.Redis().lock(lock_id, 4 * 60 + 20)
    try:
        have_lock = my_lock.acquire(blocking=False)
        if have_lock:
            print(lock_id + " lock acquired!")

            # these tokens are necessary for user authentication
            consumer_key = Auth[0]
            consumer_secret = Auth[1]
            access_key = Auth[2]
            access_secret = Auth[3]

            # create twitter API object
            auth = OAuth(access_key, access_secret, consumer_key, consumer_secret)
            twitter_stream = TwitterStream(auth=auth, secure=True, api_version=None)
            print(twitter_stream)
            # iterate over tweets matching this filter text
            # IMPORTANT! this is not quite the same as a standard twitter search
            tweet_iter = twitter_stream.statuses.filter(track=search_term)

            print("Streamming connection " + str(number) + " established")

            stopwords = loadStopWords()

            for tweet in tweet_iter:
                # try:
                # check whether this is a valid tweet
                if tweet.get('text') and tweet['lang'] == "en":

                    url_list = []
                    for url in tweet['entities']['urls']:
                        url_list.append(url['expanded_url'])

                    mention_list = []
                    for mention in tweet['entities']['user_mentions']:
                        mention_list.append("@" + mention['screen_name'].lower())

                    hashtag_list = []
                    for hashtag in tweet['entities']['hashtags']:
                        if len(hashtag) > 1:
                            hashtag_list.append("#" + hashtag['text'].lower())

                    media_urls = []
                    if 'media' in tweet['entities']:
                        media_urls = [media['media_url'] for media in tweet['entities']['media']]

                    tweet_new = Tweet(TweetID=tweet['id_str'],

                                      User="@" + tweet['user']['screen_name'],
                                      Follower=tweet['user']['followers_count'],

                                      TweetContent=tweet['text'],
                                      TweetContent_Clean=processTweet(tweet['text'], stopwords),
                                      DateTime=datetime.strptime(tweet['created_at'],
                                                                 "%a %b %d %H:%M:%S %z %Y").replace(
                                          tzinfo=utc),
                                      Urls=";".join(url_list),
                                      Mentions=";".join(mention_list),
                                      Hashtags=";".join(hashtag_list),
                                      Image=";".join(media_urls),
                                      Handled=False)

                    try:
                        tweet_new.save()
                        # print(tweet_new.TweetContent_Clean)
                    except:
                        pass

        else:
            print(lock_id + " is locked by another worker!")

    except SoftTimeLimitExceeded:
        print('Connection ' + str(number) + ' Stops!')

    except (TimeLimitExceeded, WorkerShutdown):
        print('Connection ' + str(number) + ' Stops! (TimeLimitExceeded or WorkerShutdown)')

    # except:
    # print("Unexpected error:", sys.exc_info()[0])

    finally:
        if have_lock:
            print(lock_id + " released!")
            my_lock.release()


def pollKeywords(limit, keyword_per_article, hours):
    time_threshold = datetime.utcnow().replace(tzinfo=utc) - timedelta(hours=hours)
    search_result = Article.objects.filter(DateTime__gte=time_threshold).order_by(
        '-DateTime')
    # search_result = Article.objects.filter(DateTime__gte=time_threshold, Type="RSS").order_by('-DateTime')
    print("No. articles: " + str(len(search_result)))
    keywords_poll = []
    for article in search_result.iterator():
        splited = article.Keywords.split(',')
        if len(splited) >= 3:
            # print(streamKeyword.Stream_Keywords)
            # randomed = random.sample(splited, min(keyword_per_article, len(splited)))
            keywords_poll += splited[:min(keyword_per_article, len(splited))]

    keywords_poll = list(set(keywords_poll))
    print("No. Keywords: " + str(len(keywords_poll)))
    # print(keywords_poll)
    poll_chunk = chunks(keywords_poll, limit)

    return poll_chunk

def chunks(l, n):
    chunk = []
    for i in range(0, len(l), n):
        chunk.append(','.join(l[i:i + n]))

    return chunk



def processTweet(tweet, stopwords):
    tweet = tweet.lower()
    tweet = re.sub('((www\.[\s]+)|(https?://[^\s]+))', '', tweet)
    tweet = re.sub('@[^\s]+', '', tweet)
    # tweet = re.sub('#([^\s]+)', '([^\s]+)', tweet)
    tweet = re.sub('[:;>?<=*+()./,\-#!&"$%\{˜|\}\'\[ˆ_\\@\]1234567890’‘]', ' ', tweet)
    tweet = re.sub('[\d]', '', tweet)
    tweet = removeStopWords(tweet, stopwords)
    return tweet


def removeStopWords(tweet, stopword):
    split = str.split(tweet, ' ')
    for s in split:
        if len(s) < 2 or s in stopword:
            split[split.index(s)] = ''
    tweet = ' '.join(split)
    # Remove additional white spaces
    tweet = re.sub('[\s]+', ' ', tweet)
    tweet = tweet.strip()
    return tweet


def loadStopWords():
    stopword = nltk.corpus.stopwords.words('english')
    stopword.extend(
        ['this', 'that', 'the', 'might', 'have', 'been', 'from', 'but', 'they', 'will', 'has', 'having', 'had', 'how',
         'went', 'were', 'why', 'and', 'still', 'his', 'her', 'was', 'its', 'per', 'cent', 'a', 'able', 'about',
         'across', 'after', 'all', 'almost', 'also', 'am', 'among',
         'an', 'and', 'any', 'are', 'as', 'at', 'be', 'because', 'been', 'but', 'by', 'can',
         'cannot', 'could', 'dear', 'did', 'do', 'does', 'either', 'else', 'ever', 'every',
         'for', 'from', 'get', 'got', 'had', 'has', 'have', 'he', 'her', 'hers', 'him', 'his',
         'how', 'however', 'i', 'if', 'in', 'into', 'is', 'it', 'its', 'just', 'least', 'let',
         'like', 'likely', 'may', 'me', 'might', 'most', 'must', 'my', 'neither', 'no', 'nor',
         'not', 'of', 'off', 'often', 'on', 'only', 'or', 'other', 'our', 'own', 'rather', 'said',
         'say', 'says', 'she', 'should', 'since', 'so', 'some', 'than', 'that', 'the', 'their',
         'them', 'then', 'there', 'these', 'they', 'this', 'tis', 'to', 'too', 'twas', 'us',
         'wants', 'was', 'we', 'were', 'what', 'when', 'where', 'which', 'while', 'who',
         'whom', 'why', 'will', 'with', 'would', 'yet', 'you', 'your', 've', 're', 'rt'])
    stopword = list(set(stopword))

    return stopword

#get your user authentication tokens from apps.twitter.com
def listAuth(i):
    Auth = [
                ['', '', '', ''],
                ['', '', '', ''],
                ['', '', '', ''],
       ]

    return Auth[i]
