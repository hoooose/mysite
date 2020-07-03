import threading
from django.db import models
from django.contrib.contenttypes.models import ContentType 
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.auth.models import User
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import send_mail

class SendMail(threading.Thread):
    def __init__(self, mail_title, email, html_message):
        self.mail_title = mail_title
        self.email = email
        self.html_message = html_message
        super().__init__()

    def run(self):
        send_mail(
            self.mail_title,
            '',#内容用html_message代替
            settings.EMAIL_FROM,
            [self.email],
            fail_silently=False,
            html_message=self.html_message,
            )

# Create your models here.
class Comment(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    text = models.TextField()
    comment_time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, related_name='comments',on_delete=models.CASCADE)

    reply_to = models.ForeignKey(User, related_name='replies', null=True, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', related_name='parent_comment', null=True, on_delete=models.CASCADE)
    root = models.ForeignKey('self', related_name='root_comment',null=True, on_delete=models.CASCADE)

    class Meta:
        ordering = ['comment_time']

    def __str__(self):
        return self.text

    def notice_user(self):
        # 通知用户
        if self.parent is None:
            # 评论博客或文章本身
            mail_title = '有人评论了你的博客'
            email = self.content_object.get_email()
        else:
            mail_title = '有人回复了你的评论'
            # 评论回复
            email = self.reply_to.email

        if email != '':
            context = {}
            context['mail_content'] = self.text
            context['url'] = self.content_object.get_url()
            html_message = render_to_string('comment/send_mail.html', context)

            send_mail = SendMail(mail_title, email, html_message)
            send_mail.start()
