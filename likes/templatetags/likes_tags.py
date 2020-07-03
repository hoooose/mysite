from django import template
from django.contrib.contenttypes.models import ContentType

from ..models import LikeCount, LikeRecord

register = template.Library()

@register.simple_tag
def get_liked_num(obj):
    content_type = ContentType.objects.get_for_model(obj)
    object_id = obj.pk
    like_count,created = LikeCount.objects.get_or_create(content_type=content_type, object_id=object_id)
    return like_count.liked_num

@register.simple_tag(takes_context=True)
def get_like_status(context, obj):
    content_type = ContentType.objects.get_for_model(obj)
    object_id = obj.pk
    user = context['user']

    if not user.is_authenticated:
        return ''

    if LikeRecord.objects.filter(content_type=content_type, object_id=object_id, user=user).exists():
        return 'active'
    else:
        return ''

@register.simple_tag
def get_content_type(obj):
    # 因为之前调用的是model 
    # content_type = ContentType.objects.get_for_model(obj)
    # return content_type.model
    return ContentType.objects.get_for_model(obj).model