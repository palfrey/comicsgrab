def updateComics():
    for user in ["palfrey"]: # FIXME remove hardcode
        user = get_object_or_404(User, pk=user)
        now = DateManip()
        df = ComicsDef(None,os.path.join(settings.COMICS_DIR, "cache"),module="Postgres")
        df.update(settings.COMICS_DIR,user=[user.name],now=now)