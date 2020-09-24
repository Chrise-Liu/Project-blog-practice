from django.db import models
from user.models import UserProfile

# Create your models here.

class Topic(models.Model):
    title = models.CharField(max_length=50, verbose_name='文章標題')
    # tec - 技術類  no-tec - 非技術類
    category = models.CharField(max_length=20, verbose_name='文章分類')
    # public - 公開的  private - 私有的
    limit = models.CharField(max_length=10, verbose_name='文章權限')
    introduce = models.CharField(max_length=90, verbose_name='文章簡介')
    content = models.TextField(verbose_name='文章內容')
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)
    # 外鍵
    author = models.ForeignKey(UserProfile)

    class Meta:
        db_table = 'topic'