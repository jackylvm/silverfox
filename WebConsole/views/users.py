#!/usr/bin/env python  
# -*- coding: utf-8 -*- 
# Jacky<jackylvm@foxmail.com>
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from django.views.decorators.csrf import csrf_exempt

from WebConsole.models import AuthUser


@login_required
def manage(request):
    """"""
    tpl = get_template("user/manage.html")
    return HttpResponse(tpl.render({}, request))


@login_required
@csrf_exempt
def query_all(request):
    """"""
    all = AuthUser.objects.all()
    lst = []
    for user in all:
        href = "/admin/WebConsole/authuser/{}/change/".format(user.id)
        if user.is_superuser:
            opt = '<a class="btn btn-danger btn-xs" href="{0}"> 详细信息 </a>'.format(href)
        else:
            opt = '<a class="btn btn-danger btn-xs" href="{0}"> 详细信息 </a>' \
                  '<a class="btn btn-warning btn-xs" href="{0}"> 删除 </a>'.format(href)
        lst.append([
            user.id,
            user.username,
            user.show_name,
            user.sys_user,
            user.sys_uid,
            opt,
        ])
    datas = {"success": True, "datas": lst}
    return JsonResponse(datas)
