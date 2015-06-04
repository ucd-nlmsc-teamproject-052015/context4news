from django.shortcuts import render
from articles.tasks import scrapRSSFeed
from tweets.function import twitter_stream, listAuth


def home_index(request):
    return render(request, 'homepage.html')


# def home_debug(request):
#     #scrapRSSFeed('http://www.irishtimes.com/cmlink/news-1.1319192')
#     stream_keywords = ["ireland", "dublin"] #ireland politics, ireland news, irish news"
#
#     print("Start Twitter streaming connection!")
#     #twitter_stream.apply_async((listAuth(0), stream_keywords, 1), expires=30)
#     twitter_stream(listAuth(0), stream_keywords, 1)
#
#     return render(request, 'debug.html', {"message": ""})