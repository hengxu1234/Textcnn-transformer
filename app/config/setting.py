# -*- coding: utf-8 -*-
import json

# @File    : setting
# @Date    : 2020/11/9 17:52
# @Author  : 玖月
# import os
# from concurrent.futures.thread import ThreadPoolExecutor
# import requests
from xpinyin import Pinyin

from ml.model.TextCNN import Config, Model
from ml.utils.predict_dataset_utils import LoadData
import torch

torch.set_num_threads(1)

beta_model_game = ['2016701']

class ServerConfig(object):
    # 预先加载到内存
    model_config = Config()
    data = LoadData(model_config)
    char_vocab, pinyin_vocab, strokes_vocab, char2strokes = data.load_vocab()
    model_config.vocab_size = len(char_vocab)
    model_config.pinyin_vocab_size = len(pinyin_vocab)
    model_config.strokes_vocab_size = len(strokes_vocab)

    # 实例化 Model 类
    prepare_model = Model(model_config).to('cpu')
    prepare_model.load_state_dict(torch.load(model_config.save_model_path, map_location='cpu'))

    pinyin_tool = Pinyin()


class BaseConfig(object):
    """
    基础配置
    """
    # ServerConfig
    SERVER_CONFIG = ServerConfig()
    with open('app/config/bianti_vocab.json', 'r', encoding='utf-8') as f:
        BIANTI_VOCAB = json.loads(f.readlines()[0])


class DevelopmentConfig(BaseConfig):
    """
    开发环境普通配置
    """
    DEBUG = False


class ProductionConfig(BaseConfig):
    """
    生产环境普通配置
    """
    DEBUG = False


class TestConfig(BaseConfig):
    """
    测试环境普通配置
    """
    DEBUG = False
