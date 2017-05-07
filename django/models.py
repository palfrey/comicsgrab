from django.db import models
from protobuffield import ProtobufField
import comicsgrab.strips_pb2 as pb2

class User(models.Model):
    class Meta:
        db_table = "comics_users"
    name = models.CharField(max_length=100, primary_key=True)
    pb = ProtobufField(protoclass=pb2.User)

class Strip(models.Model):
    class Meta:
        db_table = "comics_strips"
    name = models.CharField(max_length=100, primary_key=True)
    description = models.CharField(max_length=200)
    homepage = models.CharField(max_length=200)
    pb = ProtobufField(protoclass=pb2.Strip, default_args={"name":""})

class Class(models.Model):
    class Meta:
        db_table = "comics_classes"
        verbose_name_plural = "classes"
    name = models.CharField(max_length=100, primary_key=True)
    description = models.CharField(max_length=200)
    pb = ProtobufField(protoclass=pb2.Class)