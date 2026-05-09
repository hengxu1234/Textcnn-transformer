# -*- coding: utf-8 -*-

# @File    : error_code
# @Author  : 玖月
from app.libs.error import APIException


class ServerError(APIException):
    code = 500
    msg = '抱歉，服务器未知错误'
    error_code = 999


class Success(APIException):
    code = 201
    msg = '成功'
    error_code = 0


class Failed(APIException):
    code = 400
    msg = '失败'
    error_code = 9999


class NotFound(APIException):
    code = 404
    msg = '资源不存在'
    error_code = 10020


class ParameterException(APIException):
    code = 200
    msg = '参数错误'
    error_code = 1902


class QuerySuccess(APIException):
    code = 200
    msg = '成功'
    error_code = 0
