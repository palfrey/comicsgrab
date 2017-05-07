from django.conf.urls import url
import views
from django.views.static import serve
from django.conf import settings

urlpatterns = [
    url(r'^$', views.index),
    url(r'^(?P<path>[0-9]{4}-[0-9]{2}-[0-9]{2}/[^/]+)$', serve, {
            'document_root': settings.COMICS_DIR,
        }),
    url(r'^(?P<strip>.+)', views.update_strip, name="update_strip")
]