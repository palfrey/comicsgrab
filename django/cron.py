from comicsgrab.deffile import ComicsDef
from comicsgrab.date_manip import DateManip
from django.conf import settings
import os.path
from models import User

def updateComics():
    for user in User.objects.all():
        if not user.pb_decode().enabled:
            continue
        now = DateManip()
        df = ComicsDef(None,os.path.join(settings.COMICS_DIR, "cache"),module="Postgres")
        df.update(settings.COMICS_DIR,user=[user.name],now=now)