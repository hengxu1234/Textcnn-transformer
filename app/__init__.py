# -*- coding: utf-8 -*-
# @AUTHOR  : 玖月

import json

from werkzeug.urls import urlencode
import urllib.parse

import time

from flask import request, g
from flask_cors import CORS

from .app import Flask
from .libs.log import MyLog


def register_blueprint(app):
    from app.api.v1 import create_blueprint_v1
    app.register_blueprint(create_blueprint_v1(), url_prefix='/v1')


def register_before_request(app):
    @app.before_request
    def request_cost_time():
        g.request_start_time = time.time()
        g.request_time = lambda: "%.5f" % (time.time() - g.request_start_time)


def register_after_request(app):
    @app.after_request
    def log_response(resp):
        log_config = app.config.get('LOG')
        if not log_config['REQUEST_LOG']:
            return resp

        request_ip = request.headers.get("Yz-Client-Ip").split(',')[0] if request.headers.get("Yz-Client-Ip", "") else request.remote_addr
        message = '[%s] -> [%s] from:%s content-type:%s costs:%.3f ms' % (
            request.method,
            request.path,
            request_ip,
            request.content_type,
            float(g.request_time()) * 1000
        )
        if log_config['LEVEL'] == 'INFO':
            app.logger.info(message)
        elif log_config['LEVEL'] == 'DEBUG':
            req_form = '{}'
            req_body = '{}'
            try:
                if 'application/json' in request.content_type:
                    data = request.get_json(silent=True)
                    req_body = data
                    if not data:
                        body_raw = request.get_data(as_text=True)
                        # req_body = json.loads(body_raw.replace('\n', '\\n'))
                        req_body = json.loads(body_raw)
                else:
                    body_raw = request.get_data(as_text=True)
                    req_body = urllib.parse.parse_qs(body_raw)

                req_form = request.form.to_dict() if request.form else {}
            except:
                pass
            message += " data:{\n\tparam: %s, \n\tform: %s, \n\tbody: %s\n\tresponse: %s\n} " % (
                json.dumps(request.args, ensure_ascii=False).encode('utf-8'),
                req_form,
                req_body,
                resp.json
            )
            app.logger.debug(message)
        return resp


def apply_cors(app):
    CORS(app)


def create_app(env='development', register_all=True):
    app = Flask(__name__)
    app.config.from_object('app.config.setting.BaseConfig')
    if env == 'production':
        app.config.from_object('app.config.setting.ProductionConfig')
        app.config.from_object('app.config.secure.ProductionSecure')
    elif env == 'development':
        app.config.from_object('app.config.setting.DevelopmentConfig')
        app.config.from_object('app.config.secure.DevelopmentSecure')
    elif env == 'test':
        app.config.from_object('app.config.setting.TestConfig')
        app.config.from_object('app.config.secure.TestSecure')
    app.config.from_object('app.config.log')

    if register_all:
        register_blueprint(app)
        # register_plugin(app)
        MyLog(app)
        register_before_request(app)
        register_after_request(app)
        apply_cors(app)

    return app
