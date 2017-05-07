from django.contrib import admin
from models import *

@admin.register(Strip)
class Strip(admin.ModelAdmin):
    list_display = ('name', 'description', 'homepage')

@admin.register(Class)
class Class(admin.ModelAdmin):
    #list_display = ('name', 'description', 'homepage')
    pass

@admin.register(User)
class User(admin.ModelAdmin):
    list_display = ('name',)
