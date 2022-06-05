from django.conf.urls import url
from . import views
from django.views.static import serve
from django.conf import settings

urlpatterns = [
    url(r'^$', views.index),
    url(r'^(?P<path>[0-9]{4}-[0-9]{2}-[0-9]{2}/[^/]+)$', serve, {
            'document_root': settings.COMICS_DIR,
        }),
    url(r'^user/(?P<user>.+)', views.update_strips_for_user, name="update_strips_for_user"),
    url(r'^(?P<strip>.+)', views.update_strip, name="update_strip"),
]