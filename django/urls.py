from django.urls import re_path
from . import views
from django.views.static import serve
from django.conf import settings

urlpatterns = [
    re_path(r'^$', views.index),
    re_path(r'^(?P<path>[0-9]{4}-[0-9]{2}-[0-9]{2}/[^/]+)$', serve, {
            'document_root': settings.COMICS_DIR,
        }),
    re_path(r'^user/(?P<user>.+)', views.update_strips_for_user, name="update_strips_for_user"),
    re_path(r'^(?P<strip>.+)', views.update_strip, name="update_strip"),
]