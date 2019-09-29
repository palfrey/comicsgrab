from django.shortcuts import render, get_object_or_404, redirect
from comicsgrab.django.models import *
from comicsgrab.date_manip import DateManip
from django.conf import settings
import os.path
import comicsgrab.strips_pb2 as pb2
import StringIO
import comicsgrab.loader as loader
from glob import glob
from PIL import Image, ImageFile
from comicsgrab.deffile import ComicsDef
import collections
import hashlib

# See https://stackoverflow.com/a/23575424/320546
ImageFile.LOAD_TRUNCATED_IMAGES = True

def decode(pb):
    infile = StringIO.StringIO(pb)
    for item in loader.loader(infile, "__django__"):
        decoded = item
        break
    if decoded == None:
        raise Exception,user.pb
    return decoded

def index(request):
    user = request.GET.get("user")
    if user == None:
        return render(request, "comics-index.html", {"users": User.objects.all()})
    else:
        user = get_object_or_404(User, pk=user)
        today = DateManip.today()
        if 'date' not in request.GET:
            now = today
        else:
            now = DateManip.strptime("%Y-%m-%d", request.GET['date'])
        folder = now.strftime("%Y-%m-%d")
        todaypath = os.path.join(settings.COMICS_DIR, folder)

        user_decode = decode(user.pb)
        strips = collections.OrderedDict()
        for strip in sorted(user_decode.include):
            try:
                strip = Strip.objects.get(name=strip)
            except Strip.DoesNotExist:
                continue
            strip_decode = decode(strip.pb)
            items = glob(os.path.join(todaypath,"%s-*"%strip.name))
            onlyerror = len([x for x in items if not x.endswith("error")]) == 0
            item_info = {}
            hashes = []
            for item in items:
                short_path = os.path.join(folder,os.path.basename(item))
                if item.endswith("error"):
                    if onlyerror:
                        item_info[short_path] = open(item).read()
                    continue
                image = Image.open(item)
                hash = hashlib.sha1(image.tobytes()).hexdigest()
                if hash in hashes:
                    continue
                hashes.append(hash)
                dimensions = [int(x*strip_decode.zoom) for x in image.size]
                item_info[short_path] = {"width":dimensions[0], "height":dimensions[1], "hash": hash}
            if len(item_info) > 0:
                strips[strip] = {"onlyerror":onlyerror, "homepage": strip_decode.homepage, "items": sorted(item_info.items()), "desc": strip_decode.desc}

        return render(request, "comics-list.html", {
            "user": user,
            "folder": folder,
            "now": now,
            "today": today,
            "strips": strips,
            "yesterday":now.mod_days(-1).strftime("%Y-%m-%d"),
            "tomorrow":now.mod_days(+1).strftime("%Y-%m-%d")
            })

def update_strip(request, strip):
    now = DateManip()
    df = ComicsDef(None,os.path.join(settings.COMICS_DIR, "cache"),module="Postgres")
    df.update(settings.COMICS_DIR,strips=[strip],now=now)
    return redirect("/admin/comics/strip/%s/change" % strip)

def update_strips_for_user(request, user):
    user = get_object_or_404(User, pk=user)
    now = DateManip()
    df = ComicsDef(None,os.path.join(settings.COMICS_DIR, "cache"),module="Postgres")
    df.update(settings.COMICS_DIR,user=[user.name],now=now)
    return redirect("/admin/comics/user/%s/change/" % user.name)