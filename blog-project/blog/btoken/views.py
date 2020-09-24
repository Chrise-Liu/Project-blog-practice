import time

from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
import json
from user.models import UserProfile
import hashlib

def tokens(request):
    """
    創建token == 登入
    """
    if not request.method == 'POST':
        result = {'code':101,'error':'Please use POST!'}
        return JsonResponse(result)
    # 獲取前端傳過來的數據/生成token
    # 獲取-校驗密碼-生成token
    json_str = request.body
    if not json_str:
        result = {'code':102,'error':'Please give me json!'}
        return JsonResponse(result)

    json_obj = json.loads(json_str)
    username = json_obj.get('username')
    password = json_obj.get('password')
    if not username:
        result = {'code': 103, 'error': 'Please give me username!'}
        return JsonResponse(result)

    if not password:
        result = {'code': 104, 'error': 'Please give me password!'}
        return JsonResponse(result)

    ####校驗數據####
    user = UserProfile.objects.filter(username=username)
    if not user:
        result = {'code': 105, 'error': 'Username or Password is wrong!'}
        return JsonResponse(result)

    user = user[0] # username 為主鍵所以只會有一個值
    m = hashlib.md5()
    m.update(password.encode())
    if m.hexdigest() != user.password:
        result = {'code': 106, 'error': 'Username or Password is wrong!'}
        return JsonResponse(result)

    # make token
    token = make_token(username)
    result = {'code': 200, 'username': username, 'data': {'token': token.decode()}}
    return JsonResponse(result)

def make_token(username, expire=3600*24):
    # 官方jwt / 自定義jwt
    import jwt
    key = '1234567'
    now = time.time()
    payload = {'username':username, 'exp':int(now + expire)}
    return jwt.encode(payload, key, algorithm='HS256')


