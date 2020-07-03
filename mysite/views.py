from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from blog.models import Blog

from read_statistics.utils import get_seven_days_read_data, get_today_hot_data, get_yesterday_hot_data, get_7_days_hot_data


# caches default
# Create your views here.

def home(request):
    blog_content_type = ContentType.objects.get_for_model(Blog)
    read_nums, dates = get_seven_days_read_data(blog_content_type)
    # 数据缓存于数据库
    hot_data_for_7_days = cache.get('hot_data_for_7_days')
    if hot_data_for_7_days is None:
        hot_data_for_7_days = get_7_days_hot_data(blog_content_type)
        cache.set('hot_data_for_7_days', hot_data_for_7_days, 3600)#第3个值以秒为单位的有效期

    context = {}
    context['today_hot_data'] = get_today_hot_data(blog_content_type)
    context['yesterday_hot_data'] = get_yesterday_hot_data(blog_content_type)
    context['hot_data_for_7_days'] = hot_data_for_7_days
    context['dates'] = dates
    context['read_nums'] = read_nums
    return render(request, "home.html", context)

# def login(request):
#     username = request.POST.get('username', '')
#     password = request.POST.get('password', '')
#     user = auth.authenticate(request, username=username, password=password)
#     # 反向解析'home'别名
#     referer = request.META.get('HTTP_REFERER', reverse('home'))
#     if user is not None:
#         auth.login(request, user)
#         return redirect(referer)
#     else:
#         return render(request, 'error.html', {'message':'用户名或密码不正确', 'redirect_to':referer})







