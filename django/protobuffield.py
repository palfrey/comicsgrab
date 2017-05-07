from django.db import models
from django import forms
import StringIO

import comicsgrab.dumper as dumper
import comicsgrab.loader as loader

class ProtobufField(models.BinaryField):
    description = "Storage for protobuf objects"

    def __init__(self, protoclass=None, default_args={}, *args, **kwargs):
        self.protoclass = protoclass
        self.default_args = default_args
        if protoclass != None:
            self.default = protoclass(**default_args)
        kwargs['editable'] = True
        super(ProtobufField, self).__init__(*args, **kwargs)
        self.editable = True

    def deconstruct(self):
        name, protoclass, args, kwargs = models.Field.deconstruct(self)
        if 'protoclass' in kwargs:
            del kwargs['protoclass'] 
        if 'default_args' in kwargs:
            del kwargs['default_args']
        return name, protoclass, args, kwargs 
    
    def from_db_value(self, value, expression, connection, context):
        output = StringIO.StringIO()
        pb = self.protoclass.FromString(value)
        dumper.print_pb_internal(output, pb, user=False)
        return output.getvalue()
    
    def to_python(self, value):
        if value is None:
            return value

        infile = StringIO.StringIO(value)
        for item in loader.loader(infile, "__django__"):
            if item.__class__ != self.protoclass:
                raise Exception, "Bad class: %s != %s"%(item.__class__, self.protoclass)
            return self.protoclass.SerializeToString(item)

        raise Exception, value

    def formfield(self, **kwargs):
        defaults = {'widget': forms.Textarea}
        defaults.update(kwargs)
        return super(ProtobufField, self).formfield(**defaults)