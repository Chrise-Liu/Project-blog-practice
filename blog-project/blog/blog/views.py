# flie: blog/views.py
from django.http import JsonResponse


def test_api(request):
    return JsonResponse({'code':200})