from django.http import JsonResponse
from django.shortcuts import render
from tools.login_check import login_check,get_user_by_request
import json
from .models import Topic
from user.models import UserProfile
from message.models import Message

# Create your views here.

@login_check('POST','DELETE')
def topics(request, author_id):
    # 127.0.0.1:8000/v1/topics/<author_id>?category=[tec|no-tec]
    if request.method == 'GET':
        # 獲取用戶數據
        # http://127.0.0.1:5000/<username>/topics
        # author_id 被訪問的部落格博主用戶名
        # visitor 訪客 「1.登入了 2.遊客(未登入)」
        # author 博主 當前被訪問博客的博主
        authors = UserProfile.objects.filter(username=author_id)
        # 判斷是否有這個博主
        if not authors:
            result = {'code':308, 'error':'No author!'}
            return JsonResponse(result)
        # 取出結果中的博主
        author = authors[0]

        # visitor 怎麼確定？
        visitor = get_user_by_request(request)
        visitor_name = None
        if visitor:
            visitor_name = visitor.username

        # 有t_id就是詳情頁，沒有就是列表頁
        t_id = request.GET.get('t_id')
        if t_id:
            # 當前是否為 博主訪問自己的文章
            is_self = False
            # 獲取詳情
            t_id = int(t_id)
            if author_id == visitor_name:
                is_self = True
                # 博主訪問自己
                try:
                    author_topic = Topic.objects.get(id=t_id)
                except Exception as e:
                    result = {'code':312,'error':'No topic!'}
                    return JsonResponse(result)
            else:
                # 訪客訪問博主文章
                try:
                    author_topic = Topic.objects.get(id=t_id, limit='public')
                except Exception as e:
                    result = {'code':313,'error':'No topic!!'}
                    return JsonResponse(result)

            # 拼前端返回值
            res = make_topic_res(author, author_topic, is_self)
            return JsonResponse(res)

        else:
            # 獲取用戶所有博客
            category = request.GET.get('category')
            if category in ['tec','no-tec']:
                # /v1/topics/<author_id>?category=[tec|no-tec]
                if author_id == visitor_name:
                    # 博主訪問自己
                    topics = Topic.objects.filter(author_id=author_id, category=category)
                else:
                    # 訪客來了 訪客只能
                    topics = Topic.objects.filter(author_id=author_id, category=category, limit='public')

            else:
                # /v1/topics/<author_id> 用戶全量數據
                if author_id == visitor_name:
                    # 當前為博主訪問自己的博客 獲取全部數據
                    topics = Topic.objects.filter(author_id=author_id)
                else:
                    # 訪客 非博主本人 只獲取public數據
                    topics = Topic.objects.filter(author_id=author_id, limit='public')
            res = make_topics_res(author, topics)
            return JsonResponse(res)

    elif request.method == 'POST':
        # 創建用戶部落格數據
        json_str = request.body
        if not json_str:
            result = {'code':301,'error':'Please give me json!'}
            return JsonResponse(result)
        json_obj = json.loads(json_str)
        title = json_obj.get('title')
        # 防止xss注入 使用html轉譯
        import html
        title = html.escape(title)

        if not title:
            result = {'code':302,'error':'Please give me title!'}
            return JsonResponse(result)
        content = json_obj.get('content')
        if not content:
            result = {'code':303,'error':'Please give me content!'}
            return JsonResponse(result)
        # 獲取純文本文件，用於切割文章簡介
        content_text = json_obj.get('content_text')
        if not content_text:
            result = {'code':304,'error':'Please give me content_text!'}
            return JsonResponse(result)
        # 切割簡介
        introduce = content_text[:30]
        limit = json_obj.get('limit')
        if limit not in ['public', 'private']:
            result = {'code': 305, 'error': 'Your limit is wrong!'}
            return JsonResponse(result)
        category = json_obj.get('category')
        # TODO 檢查 same to 'limit'

        # 創建數據
        Topic.objects.create(title=title,
                             category=category,
                             limit=limit,
                             content=content,
                             introduce=introduce,
                             author=request.user)
        result = {'code':200,'username':request.user.username}
        return JsonResponse(result)

    elif request.method == 'DELETE':
        # 博主刪除自己的文章
        # /v1/topics/<author_id>
        # token存儲的用戶
        author = request.user
        token_author_id = author.username
        # url中傳過來的author_id必須和token中的用戶名相等
        if author_id != token_author_id:
            result = {'code':309,'error':'You can not di it!'}
            return JsonResponse(result)

        topic_id = request.GET.get('topic_id')
        try:
            topic = Topic.objects.get(id=topic_id)
        except:
            result = {'code':310,'error':'You can not di it!!'}
            return JsonResponse(result)

        #
        if topic.author.username != author_id:
            result = {'code':311,'error':'You can not di it!!!'}
            return JsonResponse(result)

        topic.delete()
        res = {'code':200}
        return JsonResponse(res)

    return JsonResponse({'code':200, 'error':'This is a test!'})

def make_topics_res(author, topics):
    res = {'code':200,'data':{}}
    data = {}
    data['nickname'] = author.nickname
    topics_list = []
    for topic in topics:
        d = {}
        d['id'] = topic.id
        d['title'] = topic.title
        d['category'] = topic.category
        d['introduce'] = topic.introduce
        d['author'] = author.nickname
        d['created_time'] = topic.created_time.strftime('%Y-%m-%d %H:%M:%S')
        topics_list.append(d)

    data['topics'] = topics_list
    res['data'] = data
    return res

def make_topic_res(author, author_topic, is_self):
    """
    拼接詳情頁 返回數據
    :param author:
    :param author_topic:
    :param is_self:
    :return:
    """
    if is_self:
        # 博主訪問自己
        # 下一篇文章：取出ID大於當前文章ID的第一個文章 且author為當前作者的
        next_topic = Topic.objects.filter(id__gt=author_topic.id, author=author).first()
        # 上一篇文章：取出ID小於當前文章ID的第最後一個文章 且author為當前作者的
        last_topic = Topic.objects.filter(id__lt=author_topic.id, author=author).last()
    else:
        # 訪客訪問博主的
        # 下一篇
        next_topic = Topic.objects.filter(id__gt=author_topic.id, author=author, limit='public').first()
        # 上一篇
        last_topic = Topic.objects.filter(id__lt=author_topic.id, author=author, limit='public').last()
    
    # 確認數據
    if next_topic:
        next_id = next_topic.id
        next_title = next_topic.title
    else:
        next_id = None
        next_title = None

    if last_topic:
        last_id = last_topic.id
        last_title = last_topic.title
    else:
        last_id = None
        last_title = None

    # 留言處理：
    all_messages = Message.objects.filter(topic=author_topic).order_by('-created_time')
    # 所有的留言
    msg_list = []
    # 留言&回覆的映射字典
    reply_dict = {}
    msg_count = 0
    # for msg in all_messages:
    #     msg_count += 1
    #     if msg.parent_message == 0:
    #         # 當前是留言
    #         msg_list.append({'id':msg.id,
    #                          'content':msg.content,
    #                          'publisher':msg.publisher,  <--錯誤：msg.publisher.nickname
    #                          'publisher_avatar':str(msg.publisher.avatar),
    #                          'created_time':msg.created_time.strftime('%Y-%m-%d'),
    #                          'reply':[]})
    for msg in all_messages:
        msg_count += 1
        if msg.parent_message == 0:
            # 當前是留言
            msg_list.append({'id': msg.id,
                             'content': msg.content,
                             'publisher': msg.publisher.nickname,
                             'publisher_avatar': str(msg.publisher.avatar),
                             'created_time': msg.created_time.strftime('%Y-%m-%d'),
                             'reply': []})
        else:
            # 當前是回覆
            reply_dict.setdefault(msg.parent_message, [])
            reply_dict[msg.parent_message].append({'msg_id':msg.id,
                                                   'content':msg.content,
                                                   'publisher':msg.publisher.nickname,
                                                   'publisher_avatar':str(msg.publisher.avatar),
                                                   'created_time':msg.created_time.strftime('%Y-%m-%d')})
    # 合併 msg_list 和 reply_dict
    for _msg in msg_list:
        if _msg['id'] in reply_dict:
            _msg['reply'] = reply_dict[_msg['id']]

    # 拼接返回
    res = {'code':200,'data':{}}
    res['data']['nickname'] = author.nickname
    res['data']['title'] = author_topic.title
    res['data']['category'] = author_topic.category
    res['data']['created_time'] = author_topic.created_time.strftime('%Y-%m-%d %H:%M:%S')
    res['data']['content'] = author_topic.content
    res['data']['introduce'] = author_topic.introduce
    res['data']['author'] = author.nickname
    res['data']['next_id'] = next_id
    res['data']['next_title'] = next_title
    res['data']['last_id'] = last_id
    res['data']['last_title'] = last_title
    # message 暫時為假數據
    # res['data']['messages'] = []
    # res['data']['messages_count'] = 0
    res['data']['messages'] = msg_list
    res['data']['messages_count'] = msg_count
    return res