from django.contrib import admin
from models import *

@admin.register(Strip)
class Strip(admin.ModelAdmin):
    list_display = ('name', 'description', 'homepage')
    change_form_template = 'admin/change_form_strip.html'
    search_fields = ["name"]

@admin.register(Class)
class Class(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ["name"]

@admin.register(User)
class User(admin.ModelAdmin):
    list_display = ('name',)
    change_form_template = 'admin/change_form_user.html'
