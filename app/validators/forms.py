import json

from flask import request
from wtforms import Form as WTForm, StringField, PasswordField, FieldList, BooleanField, FloatField
from wtforms.validators import AnyOf
from wtforms.validators import DataRequired, Length, Email, ValidationError, EqualTo, Optional
from werkzeug.urls import url_decode

from app.libs.error_code import ParameterException


class Form(WTForm):
    def __init__(self):
        if 'application/json' in request.content_type:
            data = request.get_json(silent=True)
            # print(data)
            if not data:
                body_raw = request.get_data(as_text=True)
                # data = json.loads(body_raw.replace('\n', '\\n'))
                # print(body_raw, type(body_raw))
                data = json.loads(body_raw)
        else:
            body_raw = request.get_data(as_text=True)
            data = url_decode(body_raw)

        args = request.args.to_dict()
        super(Form, self).__init__(data=data, **args)

    def validate_for_api(self):
        valid = super(Form, self).validate()
        if not valid:
            raise ParameterException(msg=self.errors)
        return self


class InferenceForm(Form):
    text = StringField('text', validators=[DataRequired(message='聊天内容不可以为空')])
    nickname = StringField('nickname', validators=[Optional()])
    # 阈值
    score_threshold = FloatField('score_threshold', validators=[DataRequired(message='阈值不可以为空')])
