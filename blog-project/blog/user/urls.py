# file: user/urls.py

from django.conf.urls import url
from . import views

urlpatterns = [
    # http://127.0.0.1:8000/v1/users
    url(r'^$', views.users),
    # http://127.0.0.1:8000/v1/users/<username>
    # APPEND_SLASH 自動補全url後面的斜線
    url(r'^/(?P<username>[\w]{1,11})$', views.users),
    # http://127.0.0.1:8000/v1/users/<username>/avatar
    url(r'^/(?P<username>[\w]{1,11})/avatar$', views.user_avatar),
]