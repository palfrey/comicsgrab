from django.contrib import admin
from models import *

@admin.register(Strip)
class Strip(admin.ModelAdmin):
    list_display = ('name', 'description', 'homepage')
    change_form_template = 'admin/change_form_strip.html'

@admin.register(Class)
class Class(admin.ModelAdmin):
    #list_display = ('name', 'description', 'homepage')
    pass

@admin.register(User)
class User(admin.ModelAdmin):
    list_display = ('name',)
