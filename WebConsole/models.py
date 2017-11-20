# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Jacky<jackylvm@foxmail.com>
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


class AuthUser(AbstractUser):
    """"""
    show_name = models.CharField(verbose_name="显示名字", max_length=128, default="", help_text="显示名")
    sys_user = models.CharField(verbose_name="操作系统用户名", max_length=128, default="", help_text="系统账号")
    sys_uid = models.IntegerField(verbose_name="操作系统UID", default=0, help_text="系统账号ID")
    kbe_root = models.CharField(verbose_name="KBE_ROOT", max_length=256, default="", help_text="kbe_root")
    kbe_res_path = models.TextField(verbose_name="KBE_RES_PATH", max_length=256, default="", help_text="kbe_res_path")
    kbe_bin_path = models.TextField(verbose_name="KBE_BIN_PATH", max_length=256, default="", help_text="kbe_bin_path")

    objects = UserManager()

    class Meta:
        """"""
        app_label = "WebConsole"


class ServerLayout(models.Model):
    """
    服务器运行配置表
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128, default="", help_text="名称", db_index=True, unique=True)
    sys_user = models.CharField(max_length=128, default="", help_text="系统账号")
    config = models.TextField(max_length=32768, default="", help_text="配置(JSON)")

    class Meta:
        """"""
        app_label = "WebConsole"
