from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.article_index, name='article_index'),
    url(r'^article_list/$', views.article_list, name='article_list'),
    url(r'^(?P<article_id>[0-9]+)/$', views.article_detail_id, name='article_detail_id')
]