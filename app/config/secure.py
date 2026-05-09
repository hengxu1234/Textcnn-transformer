# -*- coding: utf-8 -*-

# @File    : secure
# @Date    : 2020/11/9 17:52
# @Author  : 玖月


# 安全性配置
from app.config.setting import BaseConfig


class ProductionSecure(BaseConfig):
    """
    生产环境安全性配置
    """


class TestSecure(BaseConfig):
    """
    测试环境安全性配置
    """
