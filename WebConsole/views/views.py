# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Jacky<jackylvm@foxmail.com>
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import get_template

from WebConsole.forms import LoginForm
from WebConsole.models import AuthUser


@login_required
def index(request):
    """"""
    tpl = get_template('index.html')
    return HttpResponse(tpl.render({}, request))


def login(request):
    """"""
    if "GET" == request.method:
        if request.user.is_authenticated:
            if request.user.is_staff:
                return HttpResponseRedirect("/user/manage")
            return HttpResponseRedirect("/index")
        else:
            form = LoginForm()
            tpl = get_template("user/login.html")
            html = tpl.render({"form": form, "passwordIsWrong": False}, request)
            return HttpResponse(html)
    else:
        form = LoginForm(request.POST)
        if form.is_valid():
            username = request.POST.get("username", "")
            password = request.POST.get("password", "")
            user = auth.authenticate(username=username, password=password)
            if user is not None and user.is_active:
                # 设置登录session在浏览器关闭后即过期
                # request.session.set_expiry(0)

                request.session["logined"] = True
                request.session["auth_id"] = user.id
                request.session["auth_user"] = username
                request.session["auth_show_name"] = user.show_name
                request.session["sys_user"] = user.sys_user
                request.session["sys_uid"] = user.sys_uid
                request.session["auth_is_admin"] = user.is_superuser

                auth.login(request, user)
                if user.is_staff:
                    return HttpResponseRedirect("/user/manage")

                request.session["kbe_root"] = user.kbe_root
                request.session["kbe_res_path"] = user.kbe_res_path
                request.session["kbe_bin_path"] = user.kbe_bin_path
                return HttpResponseRedirect("/index")
            else:
                if not user:
                    if "admin" == username and "admin123" == password:
                        user = AuthUser.objects.create_superuser(username, "admin@admin.com", password)
                        user.show_name = username
                        user.sys_user = ""
                        user.sys_uid = 0
                        user.kbe_root = ""
                        user.kbe_res_path = ""
                        user.kbe_bin_path = ""
                        user.save()

                        auth.login(request, user)
                        return HttpResponseRedirect("/user/manage")
                    else:
                        tpl = get_template("user/login.html")
                        html = tpl.render({"form": form, "passwordIsWrong": True}, request)
                        return HttpResponse(html)
                else:
                    tpl = get_template("user/login.html")
                    html = tpl.render({"form": form, "passwordIsWrong": True}, request)
                    return HttpResponse(html)
        else:
            tpl = get_template("user/login.html")
            html = tpl.render({"form": form, "passwordIsWrong": True}, request)
            return HttpResponse(html)


def dologin(request):
    """"""
    tpl = get_template("user/login.html")
    return HttpResponse(tpl.render({}, request))


@login_required
def logout(request):
    """"""
    auth.logout(request)
    return HttpResponseRedirect("/")
