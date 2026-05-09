# -*- coding: utf-8 -*-
# @AUTHOR  : 玖月
from flask import Blueprint
from app.api.v1 import inference


def create_blueprint_v1():
    bp_v1 = Blueprint('v1', __name__)
    inference.inference_api.register(bp_v1)

    return bp_v1
