from django.shortcuts import render, redirect
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from django.db.models import ObjectDoesNotExist

from .models import LikeCount, LikeRecord

# Create your views here.
def SucessResponse(liked_num):
    data = {}
    data['status'] = 'SUCCESS'
    data['liked_num'] = liked_num
    return JsonResponse(data)

def ErrorResponse(code, message):
    data = {}
    data['status'] = 'ERROR'
    data['code'] = code
    data['message'] = message
    return JsonResponse(data)

def like_change(request):
    # 把数据取出来
    user = request.user 
    content_type = request.GET.get('content_type')
    object_id = request.GET.get('object_id')
    is_like = request.GET.get('is_like')

    # 转换数据,数据是字符串格式
    content_type = ContentType.objects.get(model=content_type)
    object_id = int(object_id)

    # 验证用户
    if not user.is_authenticated: 
        # return redirect('login.html')
        return ErrorResponse(400,'用户未登录')

    # 验证点赞对象是否存在
    try:
        model_class = content_type.model_class()
        model_obj = model_class.objects.get(pk=object_id)
    except ObjectDoesNotExist:
        return ErrorResponse(401,'评论对象不存在')

    # 处理数据
    if is_like == 'true':
        # 点赞 数量+=1 active 添加
        like_record, created = LikeRecord.objects.get_or_create(content_type=content_type, object_id=object_id, user=user)
        if created:
            # 新人点赞
            like_count, created = LikeCount.objects.get_or_create(content_type=content_type, object_id=object_id)
            like_count.liked_num += 1
            like_count.save()
            return SucessResponse(like_count.liked_num)
        else:
            # 已经点赞过 提示不能重复请求 为什么还会出现?# 改get请求?
            return ErrorResponse(code=402, message='重复点赞')
    else:
        # 取消点赞 数量-=1 active取消
        if LikeRecord.objects.filter(content_type=content_type, object_id=object_id, user=user).exists():
            # 有点赞过,取消点赞
            like_record = LikeRecord.objects.get(content_type=content_type, object_id=object_id, user=user)
            like_record.delete()
            # 点赞总数-1 有可能不存在
            like_count, created = LikeCount.objects.get_or_create(content_type=content_type, object_id=object_id)
            if not created:
                like_count.liked_num -= 1 
                like_count.save()
                return SucessResponse(like_count.liked_num)
            else:
                # 取消点赞,但是总数不存在
                return ErrorResponse(code=404, message='数据错误')
        else:
            # 没点赞过,取消点赞,提示错误
            return ErrorResponse(code=403, message='还没有点赞,无法取消点赞')


