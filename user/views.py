import random
import string
import time
from django.shortcuts import render, redirect
from django.contrib import auth
from django.contrib.auth.models import User
from django.urls import reverse
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings

from .forms import LoginForm, RegisterForm, ChangeNicknameForm, BindEmailForm, ChangePassword, ForgotPassword
from .models import Profile

def login_for_modal(request):
    login_form = LoginForm(request.POST)
    data = {}

    if login_form.is_valid():
        user = login_form.cleaned_data['user']
        auth.login(user, request)
        data['status'] = 'SUCCESS'
    else:
        data['status'] = 'ERROR' 
    return JsonResponse(data)

def login(request):
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user = login_form.cleaned_data['user']
            if user is not None:
                auth.login(request, user)
                return redirect(request.GET.get('from' , reverse('home')))
    else:
        login_form = LoginForm()
    context = {}
    context['login_form'] = login_form
    return render(request, 'user/login.html', context)

def register_wait(request):
    code = request.GET.get('code', '')
    if code:
        print(code)
        profiles = Profile.objects.filter(verification_code=code)
        print(profiles)
        if profiles:
            for profile in profiles:
                print('profile')
                if profile.user.is_active == False:
                    profile.user.is_active = True
                    profile.user.save()
                    auth.login(request, profile.user)
                    return redirect(reverse('home'))
    context = {}
    return render(request, 'user/register_wait.html', context)

def register(request):
    if request.method == 'POST':
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            username = register_form.cleaned_data['username']
            password = register_form.cleaned_data['password']
            email = register_form.cleaned_data['email']
            # 创建用户,也可以直接User实例化
            user = User(username=username, email=email, password=password, is_active=False)
            user.save()
            # 登录用户
            # user = auth.authenticate(username=username, password=password)
            # auth.login(request, user)
            # return redirect(request.GET.get('from' , reverse('home')))
            code = ''.join(random.sample( string.ascii_letters + string.digits, 6))
            profile = Profile(user=user, verification_code=code)
            profile.save()
            

            html_message = '<h3>Noe的网站账户验证</h3><p>请点击<a href="http://localhost:8000/user/register_wait/?code=%s">邮箱验证</a>以激活您的账号</P>'%code
            send_mail(
                '邮箱验证',
                '',#内容用html_message代替
                settings.EMAIL_FROM,
                [email],
                fail_silently=False,
                html_message=html_message,
            )
            return render(request, 'user/register_wait.html', {})
    else:
        register_form = RegisterForm()
    context = {}
    context['register_form'] = register_form
    return render(request, 'user/register.html', context)

def logout(request):
    auth.logout(request)
    return redirect(request.GET.get('from' , reverse('home')))

def user_info(request):
    context = {}
    return render(request, 'user/user_info.html', context)

def change_nickname(request):
    redirect_to = request.GET.get('from',reverse('home'))

    if request.method == 'POST':
        form = ChangeNicknameForm(request.POST, user=request.user)
        if form.is_valid():
            nickname_new = form.cleaned_data['nickname_new']
            profile, created = Profile.objects.get_or_create(user=request.user)
            profile.nickname = nickname_new
            profile.save()
            return redirect(redirect_to)
    else:
        form = ChangeNicknameForm()

    context = {}
    context['form'] = form
    context['page_title'] = '修改昵称'
    context['form_title'] = '修改昵称'
    context['submit_text'] = '修改'
    context['return_back_url'] = redirect_to
    return render(request, 'form.html', context)

def bind_email(request):
    redirect_to = request.GET.get('from', reverse('home'))
    data = {}

    if request.method == 'POST':
        form = BindEmailForm(request.POST, request=request)
        if form.is_valid():
            request.user.email = form.cleaned_data['email']
            request.user.save()

            # 清除session
            del request.session['bind_email']
            return redirect(redirect_to)
    else:
        form = BindEmailForm()
    context = {}
    context['form'] = form
    context['page_title'] = '修改邮箱'
    context['form_title'] = '修改邮箱'
    context['submit_text'] = '修改'
    context['return_back_url'] = redirect_to
    return render(request, 'user/bind_email.html', context)

def send_verification_code(request):
    email = request.GET.get("email", '')
    send_for = request.GET.get("send_for", '')
    data = {}

    if not email == '':
        # 生成一个6位数验证码
        code = ''.join(random.sample( string.ascii_letters + string.digits, 6))
        # 保存code
        request.session[send_for] = code
        # 设置session的时效性
        # request.session.set_expiry(10)
        now = int(time.time())
        send_code_time = request.session.get('send_code_time', 0)
        if now - send_code_time <= 0:
            data['status'] = 'ERROR'
        else:
            # context 加入html格式
            html_message = '<h1>Noe的验证</h1>您的验证码为<br>%s<br>请勿告知其他人'%code
            send_mail(
                '邮箱验证',
                '',#内容用html_message代替
                settings.EMAIL_FROM,
                [email],
                fail_silently=False,
                html_message=html_message,
            )
            data['status'] = 'SUCCESS'
    else:
        data['status'] = 'ERROR'
    return JsonResponse(data)

def change_password(request):
    redirect_to = request.GET.get('from', reverse('home'))
    if request.method == 'POST':
        form = ChangePassword(request.POST, request=request)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            user = request.user
            user.set_password(new_password)
            user.save()
            auth.login(request, user)
            return redirect(redirect_to)
    else:
        form = ChangePassword()
    context = {}
    context['form'] = form
    context['page_title'] = '修改密码'
    context['form_title'] = '修改密码'
    context['submit_text'] = '修改'
    context['return_back_url'] = redirect_to
    return render(request, 'form.html', context)

def forgot_password(request):
    redirect_to = request.GET.get('from', reverse('home'))
    if request.method == 'POST':
        form = ForgotPassword(request.POST, request=request)
        if form.is_valid():
            email = form.cleaned_data['email']
            new_password = form.cleaned_data['new_password']
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()

            # 清除session
            del request.session['forgot_password']
            return redirect(redirect_to)
    else:
        form = ForgotPassword()
    context = {}
    context['form'] = form
    context['page_title'] = '忘记密码'
    context['form_title'] = '忘记密码'
    context['submit_text'] = '修改'
    context['return_back_url'] = redirect_to
    return render(request, 'user/forgot_password.html', context)








