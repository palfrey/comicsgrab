from django.shortcuts import render, get_object_or_404
from comicsgrab.django.models import *
from comicsgrab.date_manip import DateManip
from django.conf import settings
import os.path
import comicsgrab.strips_pb2 as pb2
import StringIO
import comicsgrab.loader as loader
from glob import glob
from PIL import Image

def index(request):
    user = request.GET.get("user")
    if user == None:
        return render(request, "comics-index.html", {"users": User.objects.all()})
    else:
        user = get_object_or_404(User, pk=user)
        today = DateManip().today()
        if 'date' not in request.GET:
            now = DateManip().today()
        else:
            now = DateManip.strptime("%Y-%m-%d", request.GET['date'][0])
        folder = now.strftime("%Y-%m-%d")
        todaypath = os.path.join(settings.COMICS_DIR, folder)

        infile = StringIO.StringIO(user.pb)
        for item in loader.loader(infile, "__django__"):
            decode = item
            break
        if decode == None:
            raise Exception,user.pb

        strips = {}
        for strip in decode.include:
            items = glob(os.path.join(todaypath,"%s-*"%strip))
            onlyerror = len([x for x in items if not x.endswith("error")]) == 0
            for item in items:
                if item.endswith("error"):
                    strips[item] = open(item).read()
                    continue
                dimensions = [x*strip.zoom for x in Image.open(item).size]
                strips[item] = {"width":dimensions[0], "height":dimensions[1]}

        return render(request, "comics-list.html", {
            "user": user,
            "folder": folder,
            "now": now,
            "today": today,
            "strips": strips,
            "yesterday":now.mod_days(-1).strftime("%Y-%m-%d"),
            "tommorrow":now.mod_days(+1).strftime("%Y-%m-%d")
            })