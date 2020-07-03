from django import forms
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models import ObjectDoesNotExist
from django.contrib import auth
from ckeditor.widgets import CKEditorWidget
from .models import Comment


class CommentForm(forms.Form):
    content_type = forms.CharField(widget=forms.HiddenInput)
    object_id = forms.IntegerField(widget=forms.HiddenInput)
    text = forms.CharField(widget=CKEditorWidget(config_name='comment_ckeditor'),
                            error_messages={'required':'评论内容不能为空'})
    reply_comment_id = forms.IntegerField(widget=forms.HiddenInput(attrs={"id":"reply_comment_id"}))
    def __init__(self, *args, **kwargs):
        # 获取user
        if 'user' in kwargs:
            # pop拿掉?
            self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

    def clean(self):
        # 数据检查
        if self.user.is_authenticated:
            self.cleaned_data['user'] = self.user
        else:
            raise forms.ValidationError('用户未登录')

        text = self.cleaned_data['text']
        if text == '':
            raise forms.ValidationError('评论内容为空')
        # 评论对象不存在
        content_type = self.cleaned_data['content_type']
        model_class = ContentType.objects.get(model=content_type).model_class()
        try:
            object_id = self.cleaned_data['object_id']
            model_obj = model_class.objects.get(pk=object_id)
            self.cleaned_data['content_object'] = model_obj
        except ObjectDoesNotExist:
            raise forms.ValidationError('评论对象不存在') 
        return self.cleaned_data

    def clean_reply_comment_id(self):
        reply_comment_id = self.cleaned_data['reply_comment_id']
        if reply_comment_id < 0:
            raise forms.ValidationError('回复出错')
        elif reply_comment_id == 0:
            self.cleaned_data['parent'] = None
        elif Comment.objects.filter(pk=reply_comment_id).exists():
            parent = Comment.objects.get(pk=reply_comment_id)
            self.cleaned_data['parent'] = parent

        else:
            raise forms.ValidationError('回复出错')

        return self.cleaned_data



