#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author: kaiic
@Email: 1606155072@qq.com
@File: auth.py
@Date: 2021/11/10 15:19
@Desc: 
"""

import time

from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication
from django.core.exceptions import ObjectDoesNotExist

from K_AUTOTESTING.settings import INVALID_TIME
from k_user import models
import logging
logger = logging.getLogger('django')


class MyAuthenticationFailed(exceptions.AuthenticationFailed):
    """
    重写AuthenticationFailed
    直接把传入内容等价于detail，不做处理
    (把原本APIException内把detail数据转成str的功能禁用,使success响应类型为boolean)
    """
    def __init__(self, detail=None, code=None):
        if detail is None:
            detail = self.default_detail
        if code is None:
            code = self.default_code
        self.detail = detail

    def get_codes(self):
        """
        :return:{'code': 'authentication_failed', 'msg': 'authentication_failed', 'success': 'authentication_failed'}
        """
        if isinstance(self.detail,dict):
            ret = {
                key: self.default_code
                for key in self.detail.keys()
            }
            return ret

    def get_full_details(self):
        """
        :return: {'code': {'message': ErrorDetail(string='9999', code='authentication_failed'), 'code': 'authentication_failed'},
                    'msg': {'message': ErrorDetail(string='Token已过期，请重新登录', code='authentication_failed'),
                    'code': 'authentication_failed'},
                'success': {'message': ErrorDetail(string='False', code='authentication_failed'), 'code': 'authentication_failed'}}
        """
        if isinstance(self.detail,dict):
            ret = {
                key: {"message": exceptions.ErrorDetail(value, self.default_code), "code": self.default_code}
                for key, value in self.detail.items()
            }
            return ret


class Authenticator(BaseAuthentication):
    """
    账户鉴权认证 token
    """

    def authenticate(self, request):
        token = request.query_params.get("token", None)  # 个人用户token
        role = request.query_params.get("role", None)  # 是否管理员0:非管理员，1:管理员
        current_time = int(time.time())  # 当前时间
        # 正常用户登录访问

        try:
            user_token_data = models.UserToken.objects.get(token=token)
        except ObjectDoesNotExist:
            raise MyAuthenticationFailed({
                'code': '9999',
                'msg': 'Token已过期，请重新登录',
                'success': False
            })

        # 用户信息
        user = user_token_data.user
        # 判断 是否是管理员
        if role is None or eval(role) != user.isadmin:
            permission_verification = False
        else:
            permission_verification = True

        if not user or not permission_verification:
            raise MyAuthenticationFailed({
                "code": "9998",
                "msg": "用户未认证",
                "success": False
            })

        update_time = int(user_token_data.update_time.timestamp())

        if current_time - update_time >= INVALID_TIME and token in (None, ""):
            raise MyAuthenticationFailed({
                "code": "9997",
                "msg": "登陆超时，请重新登陆",
                "success": False
            })

        # valid update valid time
        user_token_data.token = token
        user_token_data.save()

        return user_token_data.user, user_token_data

    def authenticate_header(self, request):
        return 'Auth Failed'