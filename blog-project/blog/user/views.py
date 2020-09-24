import json
import time

from django.http import JsonResponse
from django.shortcuts import render
from .models import *
import hashlib
from btoken.views import make_token
from tools.login_check import login_check

# Create your views here.

@login_check('PUT')
def users(request, username=None):
    if request.method == 'GET':
        # 獲取用戶數據
        if username:
            # /v1/users/<username>
            # 拿指定用戶數據
            try:
                user = UserProfile.objects.get(username=username)
            except Exception as e:
                user = None
            if not user:
                result = {'code':208, 'error':'There is no user!'}
                return JsonResponse(result)
            # 檢查是否有帶查詢字符串
            if request.GET.keys():
                # 查詢指定字符串
                data = {}
                for k in request.GET.keys():
                    if hasattr(user, k):
                        v = getattr(user, k)
                        if k == 'avatar':
                            data[k] = str(v)
                        else:
                            data[k] = v
                result = {'code':200,'username':username,'data':data}
                return JsonResponse(result)
            else:
                # 全量查詢「password email 不給」
                result = {'code':200, 'username':username, 'data':{'info':user.info, 'sign':user.sign, 'avatar':str(user.avatar), 'nickname':user.nickname}}
                return JsonResponse(result)
            return JsonResponse({'code': 200,'error':'GET accept! %s'%(username)})
        else:
            return JsonResponse({'code': 200,'error':'GET accept!'})
    elif request.method == 'POST':
        # request.POST只能提取'表單POST'的數據，json格式使用request.body
        # 創建用戶
        # 前端註冊地址 http://127.0.0.1:5000/register
        json_str = request.body
        if not json_str:
            result = {'code':201, 'error':'Please give me data!'}
            return JsonResponse(result)
        json_obj = json.loads(json_str)

        username = json_obj.get('username')
        if not username:
            result = {'code':202, 'error':'Please give me username!'}
            return JsonResponse(result)

        email = json_obj.get('email')
        if not email:
            result = {'code': 203, 'error': 'Please give me email!'}
            return JsonResponse(result)

        password_1 = json_obj.get('password_1')
        password_2 = json_obj.get('password_2')
        if not password_1 or not password_2:
            result = {'code': 204, 'error': 'Please give me password!'}
            return JsonResponse(result)

        if password_1 != password_2:
            result = {'code': 205, 'error': 'password_1&2 are not the same!'}
            return JsonResponse(result)

        # 優先查詢一下用戶名是否已經存在
        old_users = UserProfile.objects.filter(username=username)
        if old_users:
            result = {'code': 206, 'error': 'User is already existed!'}
            return JsonResponse(result)

        # 密碼處理 md5 哈希/散列 不要說加密！
        m = hashlib.md5()
        m.update(password_1.encode())
        #======charfild 盡量避免使用 null=True
        sign = info = ''
        try:
            UserProfile.objects.create(username=username, nickname=username, email=email, password=m.hexdigest(), sign=sign, info=info)
        except Exception as e:
            # 報錯可能：用戶名已存在！因為可能別人比你更快註冊一樣的名子or數據庫當機
            result = {'code':207,'error':'Server is busy!'}
            return JsonResponse(result)

        # make token
        token = make_token(username)

        # 正常返回給前端
        result = {'code':200, 'username':username, 'data':{'token':token.decode()}}
        return JsonResponse(result)

    elif request.method == 'PUT':
        # 更新數據
        # 此頭可以獲取前端傳來的token
        # META可拿去http協議原生頭，META也是類字典對象可使用字典相關方法
        # 特別注意 http頭有可能被django重新命名，建議上網google
        token = request.META.get('HTTP_AUTHORIZATION')
        user = request.user
        json_str = request.body
        if not json_str:
            result = {'code':209,'error':'Please give json!'}
            return JsonResponse(result)
        json_obj = json.loads(json_str)

        if 'sign' not in json_obj:
            result = {'code': 210, 'error': 'No sign!'}
            return JsonResponse(result)
        if 'info' not in json_obj:
            result = {'code': 211, 'error': 'No info!'}
            return JsonResponse(result)

        sign = json_obj.get('sign')
        info = json_obj.get('info')

        request.user.sign = sign
        request.user.info = info
        request.user.save()
        result = {'code':200, 'username':request.user.username}
        return JsonResponse(result)
    else:
        raise
    return JsonResponse({'code':200})

# 校驗token
@login_check('POST')
def user_avatar(request, username):
    '''
    上傳用戶大頭照
    '''
    if request.method != 'POST':
        result = {'code':212,'error':'I need post!'}
        return JsonResponse(result)
    avatar = request.FILES.get('avatar')
    if not avatar:
        result = {'code':213,'error':'I need avatar!'}
        return JsonResponse(result)
    # TODO 判斷url中的username是否跟token中的username一致，若不一致，則返回error
    request.user.avatar = avatar
    request.user.save()
    result = {'code':200,'username':request.user.username}
    return JsonResponse(result)

    return JsonResponse({'code':200,'error':'This is avatar!'})