from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^$', views.post_list),
    url(r'^post/(?P<pk>[0-9]+)/$', views.post_detail, name='post_detail'),
    url(r'^post/new/$', views.post_new, name='post_new'),
    url(r'^post/(?P<pk>[0-9]+)/edit/$', views.post_edit, name='post_edit'),
    url(r'^delete/(?P<pk>[0-9]+)/$', views.post_delete, name='post_delete'),
    url(r'^export/xls/$', views.export_posts_xls, name='export_posts_xls'),
    url(r'^import/xls/$', views.import_posts_xls, name='import_posts_xls'),
]