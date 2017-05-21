from django.db import models
from protobuffield import ProtobufField
import comicsgrab.strips_pb2 as pb2
import StringIO
import comicsgrab.loader as loader

class User(models.Model):
    class Meta:
        db_table = "comics_users"
    name = models.CharField(max_length=100, primary_key=True)
    pb = ProtobufField(protoclass=pb2.User)

    def pb_decode(self):
        infile = StringIO.StringIO(self.pb)
        for item in loader.loader(infile, "__django__"):
            return item
        raise Exception

    def __str__(self):
        return self.name

class Strip(models.Model):
    class Meta:
        db_table = "comics_strips"
    name = models.CharField(max_length=100, primary_key=True)
    description = models.CharField(max_length=200)
    homepage = models.CharField(max_length=200)
    pb = ProtobufField(protoclass=pb2.Strip, default_args={"name":""})

    def __str__(self):
        return self.name

class Class(models.Model):
    class Meta:
        db_table = "comics_classes"
        verbose_name_plural = "classes"
    name = models.CharField(max_length=100, primary_key=True)
    description = models.CharField(max_length=200)
    pb = ProtobufField(protoclass=pb2.Class)

    def __str__(self):
        return self.name