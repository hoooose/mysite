import datetime
from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum
from django.utils import timezone
from .models import ReadNum, ReadDetail
from blog.models import Blog

def read_statistics_once_read(request, obj):
    ct = ContentType.objects.get_for_model(obj)
    key = '%s_%s_read'%(ct.model, obj.pk)

    if not request.COOKIES.get(key):
        # 总阅读+=1
        readnum, created = ReadNum.objects.get_or_create(content_type=ct, object_id=obj.pk)
        readnum.read_num += 1
        readnum.save()

        # 单个日期阅读+1
        date = timezone.now().date()
        readdetail, created = ReadDetail.objects.get_or_create(content_type=ct, object_id=obj.pk, date=date)
        readdetail.read_num += 1
        readdetail.save()

    return key

def get_seven_days_read_data(content_type):
    # 首页7天阅读数据
    today= timezone.now().date()
    read_nums = []
    dates = []
    for i in range(6, -1, -1):
        date = today - datetime.timedelta(days=i)
        dates.append(date.strftime('%m-%d'))
        readdetail = ReadDetail.objects.filter(content_type=content_type, date=date)
        result = readdetail.aggregate(read_num_sum=Sum('read_num'))
        # 消除None
        read_nums.append(result['read_num_sum'] or 0)

    return read_nums, dates

def get_today_hot_data(content_type):
    # 今日阅读量最多的
    today = timezone.now().date()
    read_details = ReadDetail.objects.filter(content_type=content_type, date=today).order_by('-read_num')
    return read_details[:7]

def get_yesterday_hot_data(content_type):
    # 昨日阅读量最多的
    today = timezone.now().date()
    date = today - datetime.timedelta(days=1)
    read_details = ReadDetail.objects.filter(content_type=content_type, date=date).order_by('-read_num')
    return read_details[:7]

def get_7_days_hot_data(content_type):
    # 7天阅读量最多的
    today = timezone.now().date()

    date = today - datetime.timedelta(days=7)
    # 先分组,将7天内同一blog的阅读数据区分,然后将阅读总数注释给他
    # values不懂
    read_details = Blog.objects.filter(read_detail__date__lt=today, read_detail__date__gte=date)\
                                                    .values('pk', 'title')\
                                                    .annotate(read_num_sum=Sum('read_detail__read_num'))\
                                                    .order_by('-read_num_sum')
    return read_details[:7]
