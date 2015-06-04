from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.tweet_index, name='tweet_index'),
    url(r'^tweet_list/$', views.tweet_list, name='tweet_list')

]