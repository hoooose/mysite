from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='昵称')
    nickname = models.CharField(max_length=10, default='')
    verification_code = models.CharField(max_length=10, default='')

    def __str__(self):
        return '<Profile:%s for %s>'%(self.nickname, self.user)

def get_nickname(self):
    if Profile.objects.filter(user=self).exists():
        profile = Profile.objects.get(user=self)
        return profile.nickname
    else:    
        return ''

def get_nickname_or_username(self):
    if Profile.objects.filter(user=self).exists():
        profile = Profile.objects.get(user=self)
        if not profile.nickname == '':
            return profile.nickname
    return self.username

def has_nickname(self):
    if Profile.objects.filter(user=self).exists():
        return True
    else:
        return False


User.get_nickname = get_nickname 
User.get_nickname_or_username = get_nickname_or_username
User.has_nickname = has_nickname 



