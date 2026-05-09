# -*- coding: utf-8 -*-

# @File    : error
# @Author  : 玖月
import uuid

from flask import request, json
from werkzeug.exceptions import HTTPException


class APIException(HTTPException):
    code = 500
    msg = 'sorry, we made a mistake (*￣︶￣)!'
    error_code = 999

    def __init__(self, msg=None, code=None, error_code=None, status=0, data=None, headers=None):
        if code:
            self.code = code
        if error_code:
            self.error_code = error_code
        if msg:
            self.msg = msg
        if status:
            self.status = status
        self.data = data
        self.requestId = str(uuid.uuid1())
        super(APIException, self).__init__(msg, None)

    def get_body(self, environ=None, scope=None):
        # request = request.method + ' ' + self.get_url_no_param()
        body = dict(
            message=self.msg,
            code=self.error_code,
            requestId=self.requestId
        )
        if self.data or self.data == []:
            body['data'] = self.data
        text = json.dumps(body,  ensure_ascii=False)
        return text

    def get_headers(self, environ=None, scope=None):
        """Get a list of headers."""
        return [('Content-Type', 'application/json')]

    @staticmethod
    def get_url_no_param():
        full_path = str(request.full_path)
        main_path = full_path.split('?')
        return main_path[0]
