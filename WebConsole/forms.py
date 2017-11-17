#!/usr/bin/env python  
# -*- coding: utf-8 -*- 
# Jacky<jackylvm@foxmail.com>
from django import forms


class LoginForm(forms.Form):
    """"""
    username = forms.CharField(required=True,
                               label="",
                               error_messages={"required": "请输入用户名"},
                               widget=forms.TextInput(attrs={"placeholder": "User Name", "class": "form-control"}))
    password = forms.CharField(required=True,
                               label="",
                               error_messages={"required": "密码"},
                               widget=forms.PasswordInput(
                                   attrs={"placeholder": "Password", "class": "form-control"}))

    def clean(self):
        """"""
        if not self.is_valid():
            raise forms.ValidationError("字段必须填写")
        else:
            cleaned_data = super(LoginForm, self).clean()
