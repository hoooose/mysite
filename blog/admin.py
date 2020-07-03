from django.contrib import admin
from .models import Blog, BlogType

# Register your models here.
@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "author", "get_read_num","is_deleted", "created_time",)
    ordering = ("id",)

@admin.register(BlogType)
class BlogTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "type_name",)


# @admin.register(ReadNum)
# class ReadNumAdmin(admin.ModelAdmin):
#     list_display = ("read_num", "blog",)

