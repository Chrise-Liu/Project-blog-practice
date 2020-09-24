from django.shortcuts import render
from django.http import JsonResponse
from tools.login_check import login_check
import json
from topic.models import Topic
from .models import Message

# Create your views here.

@login_check('POST')
def messages(request, topic_id):
    if request.method != 'POST':
        result = {'code':401,'error':'Please use POST!'}
        return JsonResponse(result)

    # 發表留言/回覆
    user = request.user
    json_str = request.body
    json_obj = json.loads(json_str)
    content = json_obj.get('content')
    if not content:
        result = {'code':402,'error':'Please give me content!'}
        return JsonResponse(result)
    parent_id = json_obj.get('parent_id', 0)

    try:
        topic = Topic.objects.get(id=topic_id)
    except:
        # topic被刪除or當前topic_id不真實
        result = {'code':403,'error':'No topic!'}
        return JsonResponse(result)

    # 私有博客 只能 博主留言
    if topic.limit == 'private':
        # 檢查身份
        if user.username != topic.author.username:
            result = {'code':404,'error':'Please get out!'}
            return JsonResponse(result)

        # 創建數據
        Message.objects.create(content=content, publisher=user, topic=topic, parent_message=parent_id)
        return JsonResponse({'code':200,'data':{}})