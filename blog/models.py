from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from ckeditor_uploader.fields import RichTextUploadingField
from read_statistics.models import ReadNumExpandMethod, ReadDetail


# Create your models here.
class BlogType(models.Model):
    type_name = models.CharField(max_length=15)

    def __str__(self):
        return self.type_name

class Blog(models.Model, ReadNumExpandMethod):
    title = models.CharField(max_length=30)
    # 关联上一个
    blog_type = models.ForeignKey(BlogType, on_delete=models.CASCADE)
    content = RichTextUploadingField()
    created_time = models.DateTimeField(auto_now_add=True)
    last_upgrate_time = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    is_deleted = models.BooleanField(default=False)
    # 反向关联
    read_detail = GenericRelation(ReadDetail)

    def __str__(self):
        return f'<Blog:{self.title}>'

    class Meta:
        ordering = ['-created_time']

    def get_email(self):
        return self.author.email

    def get_url(self):
        return 'blog/' + str(self.pk)

'''
class ReadNum(models.Model):
    read_num = models.IntegerField(default=0)
    blog = models.OneToOneField(Blog, on_delete=models.CASCADE) #一对一ForeignKey
'''