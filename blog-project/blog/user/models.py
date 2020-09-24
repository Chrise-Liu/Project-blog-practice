from django.db import models

# Create your models here.

# class --> UserProfile
# 表名：user_profile
# 表屬性： username, nickname, email, password, sign, info, avatar

class UserProfile(models.Model):
    username = models.CharField(max_length=11, verbose_name='用戶名', primary_key=True)
    nickname = models.CharField(max_length=30, verbose_name='暱稱')
    email = models.CharField(max_length=50, verbose_name='信箱', null=True)
    password = models.CharField(max_length=32, verbose_name='密碼')
    sign = models.CharField(max_length=50, verbose_name='個性簽名')
    info = models.CharField(max_length=150, verbose_name='個人描述')
    avatar = models.ImageField(upload_to='avatar/')

    class Meta:
        db_table = 'user_profile'