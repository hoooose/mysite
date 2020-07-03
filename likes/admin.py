from django.contrib import admin
from .models import LikeRecord

# Register your models here.
@admin.register(LikeRecord)
class LikeRecordAdmin(admin.ModelAdmin):
    list_display = ('pk', 'content_object', 'user', 'liked_time')