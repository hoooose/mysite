from django.contrib import admin
from .models import Comment 

# Register your models here.
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display=('pk', 'user', 'reply_to','text', 'comment_time', 'content_object', 'parent', 'root')
