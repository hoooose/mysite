from django import forms
from django.contrib import auth
from django.contrib.auth.models import User

class LoginForm(forms.Form):
    username_or_email = forms.CharField(label='用户名或邮箱', widget=forms.TextInput(\
                                                                    attrs={'class':'form-control', 'placeholder':'请输入用户名或邮箱'}) )
    password = forms.CharField(label='密码', widget=forms.PasswordInput(\
                                                                    attrs={'class':'form-control', 'placeholder':'请输入密码'}))

    def clean(self):
        # is_valid会调用
        username_or_email = self.cleaned_data['username_or_email']
        password = self.cleaned_data['password']

        user = auth.authenticate(username=username_or_email, password=password)
        if user is None:
            if User.objects.filter(email=username_or_email).exists():
                username = User.objects.get(email=username_or_email).username
                user = auth.authenticate(username=username, password=password)
                if not user is None:
                    self.cleaned_data["user"] = user
                    return self.cleaned_data
            raise forms.ValidationError('用户名或者密码不正确')
        else:
            self.cleaned_data["user"] = user
        return self.cleaned_data

class RegisterForm(forms.Form):
    username = forms.CharField(label='用户名', max_length=30, min_length=3, widget=forms.TextInput(\
                                                                    attrs={'class':'form-control', 'placeholder':'请输入3~30位用户名'}) )
    password = forms.CharField(label='密码', min_length=6, widget=forms.PasswordInput(\
                                                                    attrs={'class':'form-control', 'placeholder':'请输入密码'}))
    password_again = forms.CharField(label='密码确认', min_length=6, widget=forms.PasswordInput(\
                                                                    attrs={'class':'form-control', 'placeholder':'请再次输入密码'}))
    email = forms.EmailField(label='邮箱', widget=forms.EmailInput(\
                                                                    attrs={'class':'form-control', 'placeholder':'请输入邮箱'}))

    def clean_username (self):
        # 用户名规则,重复,密码规则
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).count():
            raise forms.ValidationError('用户名已存在')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).count():
            raise forms.ValidationError('邮箱已经使用')
        return email

    def clean_password_again(self):
        password = self.cleaned_data['password']
        password_again = self.cleaned_data['password_again']
        if password != password_again:
            raise forms.ValidationError('密码输入不一致')
        return password_again

class ChangeNicknameForm(forms.Form):
    nickname_new = forms.CharField(label='新的昵称', max_length=20, widget=forms.TextInput(\
                                                                    attrs={'class':'form-control','placeholder':'请输入新的昵称'}))

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

    def clean(self):
        if not self.user.is_authenticated:
            raise forms.ValidationError('用户未登录')
        return self.cleaned_data

    def clean_nickname_new(self):
        nickname_new = self.cleaned_data['nickname_new'].strip()
        if nickname_new == '':
            raise forms.ValidationError('新昵称不能为空')
        return nickname_new

class BindEmailForm(forms.Form):
    email = forms.EmailField(label='邮箱', widget=forms.EmailInput(\
                                                                    attrs={'class':'form-control', 'placeholder':'请输入邮箱'}))
    verification_code = forms.CharField(label='验证码', required=False, max_length=6, widget=forms.TextInput(\
                                                                    attrs={'class':'form-control', 'placeholder':'请输入验证码'}))

    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        super().__init__(*args, **kwargs)

    def clean(self):
        if not self.request.user.is_authenticated:
            raise forms.ValidationError('用户未登录')

        # 验证码
        code = self.request.session.get('bind_email', '')
        verification_code = self.cleaned_data.get('verification_code', '')

        if not (code == '' and verification_code == code):
            raise forms.ValidationError('验证码不正确')

    def clean_email(self):
        email = self.cleaned_data['email']
        if not '@' in email or not ".com" in email:
            raise forms.ValidationError('邮箱格式不正确')
        if User.objects.filter(email=email).count():
            raise forms.ValidationError('邮箱已经被使用')
        return email

    def clean_verification_code(self):
        verification_code = self.cleaned_data['verification_code']
        if verification_code == '':
            raise forms.ValidationError('验证码不能为空') 
        return verification_code    

class ChangePassword(forms.Form):
    old_password = forms.CharField(label='原密码', min_length=6, widget=forms.PasswordInput(
                                                                    attrs={'class':'form-control', 'placeholder':'请输入原密码'}))
    new_password = forms.CharField(label='新密码', min_length=6, widget=forms.PasswordInput(
                                                                    attrs={'class':'form-control', 'placeholder':'请输入新密码'}))
    new_password_again = forms.CharField(label='确认新密码', min_length=6, widget=forms.PasswordInput(
                                                                    attrs={'class':'form-control', 'placeholder':'请再次输入新密码'}))

    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        super().__init__(*args, **kwargs)

    def clean(self):
        old_password = self.cleaned_data.get('old_password', '')
        new_password = self.cleaned_data.get('new_password', '')
        new_password_again = self.cleaned_data.get('new_password_again', '')

        if not self.request.user.is_authenticated:
            raise forms.ValidationError('用户未登录')

        # 检查原密码
        # user.check_password(old_password)
        user = auth.authenticate(username=self.request.user.username, password=old_password)
        if user is None:
            raise forms.ValidationError('原密码不正确')

        if new_password != new_password_again or new_password == '':
            raise forms.ValidationError('两次密码输入不一致')

        return self.cleaned_data

class ForgotPassword(forms.Form):
    email = forms.EmailField(label='邮箱', widget=forms.EmailInput(
                                                                    attrs={'class':'form-control', 'placeholder':'请填写绑定的邮箱'}))
    verification_code = forms.CharField(label='验证码', widget=forms.TextInput(
                                                                    attrs={'class':'form-control', 'placeholder':'请填写邮箱验证码'}))
    new_password = forms.CharField(label='新密码', widget=forms.PasswordInput(
                                                                    attrs={'class':'form-control', 'placeholder':'请填写新密码'}))

    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        super().__init__(*args, **kwargs)

    def clean(self):
        email = self.cleaned_data['email']
        verification_code = self.cleaned_data['verification_code']
        new_password = self.cleaned_data['new_password']

        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError('邮箱未被使用')

        code = self.request.session.get('forgot_password', '')
        if verification_code != code or verification_code == '':
            raise forms.ValidationError('验证码错误')

        if new_password == '':
            raise forms.ValidationError('新密码不能为空')

        return self.cleaned_data









