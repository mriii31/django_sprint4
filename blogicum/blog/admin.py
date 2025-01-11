from django.contrib import admin

from .models import Location, Category, Post, Comment #1.1 Модели Category, Location, Post, Comment зарегистрированы в админке.

admin.site.register(Location)
admin.site.register(Category)
admin.site.register(Post)
admin.site.register(Comment)
