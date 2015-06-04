from django.shortcuts import render

# Create your views here.
import urllib
import json
import copy

from django.http import HttpResponse
from articles.models import Article

from django.shortcuts import render, get_object_or_404
from django.utils.timezone import utc
from datetime import timedelta, datetime


def article_index(request):
    return HttpResponse("Hello, world. You're at the articles index view.")


def article_detail_id(request, article_id):
    article = Article.objects.filter(pk=article_id).first()
    if not article:
        return render(request, 'article_detail.html', {'error_message': "Article reading error."})

    else:
        return render(request, 'article_detail.html',
                      {'article': article})


def article_list(request):
    try:

        th = datetime.now().replace(tzinfo=utc) - timedelta(hours=24)
        list_of_articles = Article.objects.filter(DateTime__gte=th).order_by('-DateTime')

        return render(request, 'article_list.html',
                      {'latest_articles_list': list_of_articles, 'total': len(list_of_articles)})
    except:
        return render(request, 'article_list.html')