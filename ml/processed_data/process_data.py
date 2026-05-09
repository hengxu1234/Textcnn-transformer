# -*- coding: utf-8 -*-
"""
@Author  : 玖月
@File    : process_data.py
@Date    : 2021/8/4 20:54
@Desc    : 
"""
import json
import re
from random import shuffle

from tqdm import tqdm
from zhconv import convert

import sys
import os

# 获取当前文件所在目录的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))

# 获取项目根目录（找到app所在的目录）
# 以下代码会自动定位到app的父目录（项目根目录）
current_file_path = os.path.abspath(__file__)  # 得到当前脚本的绝对路径
subdir_path = os.path.dirname(current_file_path)  # 得到subdir的路径
project_root = os.path.dirname(subdir_path)  # 得到project根目录（app的父目录）

# 将项目根目录添加到Python的搜索路径
sys.path.append(project_root)

from utils.tokenizer import AllTokenizer

# 使用绝对路径读取bianti_vocab.json文件
app_config_path = os.path.join(os.path.dirname(project_root), 'app', 'config', 'bianti_vocab.json')
bianti_vocab = json.loads(open(app_config_path, 'r', encoding='utf-8').read())


# 使用绝对路径读取old_train.txt文件
all_data = [i for i in open(os.path.join(current_dir, 'old_train.txt'), 'r', encoding='utf-8').readlines()]
data_len = len(all_data)

print(len(all_data))
# #
shuffle(all_data)
shuffle(all_data)
shuffle(all_data)
shuffle(all_data)
shuffle(all_data)

tokenizer = AllTokenizer()

# #
#
# # with open('all_data.txt', 'a', encoding='utf-8') as all_f:
# #     for i in all_data:
# #         all_f.write(i + '\n')
# #


# 使用绝对路径写入train.txt文件
with open(os.path.join(current_dir, 'train.txt'), 'w', encoding='utf-8') as f:
    for i in all_data[: int(data_len*0.8)]:
        # print(i)
        text, label = i.split('\t')
        # if text == 'Ｍｑｈ２ 栖 ６':
        #     print(i)
        #     print(convert(text, 'zh-cn').strip().replace(' ', '').replace('\n', '').replace('\r\n', '').replace(' ', '').lower())
        text = convert(text, 'zh-cn').strip().replace(' ', '').replace('\n', '').replace('\r\n', '').replace(' ', '').lower()
        # format_text = text.copy()

        char_list = []
        for char in text:
            if bianti_vocab.get(char, None):
                text = text.replace(char, bianti_vocab[char])
                # text = text.replace(char, ServerConfig.bianti_vocab[char])
                char_list.append(bianti_vocab[char])
            else:
                char_list.append(char)

        text = ''.join(char_list)

        text = tokenizer.tokenize(text)
        text = ''.join(text)
        if text:
            f.write(text + '\t' + label)
#
#
# 使用绝对路径写入dev.txt文件
with open(os.path.join(current_dir, 'dev.txt'), 'w', encoding='utf-8') as f:
    for i in all_data[int(data_len*0.8): int(data_len*0.9)]:
        text, label = i.split('\t')
        # for k, v in bianti.items():
        #     text = text.replace(k, v)
        text = convert(text, 'zh-cn').strip().replace(' ', '').replace('\n', '').replace('\r\n', '').replace(' ', '').lower()
        char_list = []
        for char in text:
            if bianti_vocab.get(char, None):
                text = text.replace(char, bianti_vocab[char])
                # text = text.replace(char, ServerConfig.bianti_vocab[char])
                char_list.append(bianti_vocab[char])
            else:
                char_list.append(char)

        text = ''.join(char_list)
        text = tokenizer.tokenize(text)
        text = ''.join(text)
        if text:
            f.write(text + '\t' + label)
#
#
# 使用绝对路径写入test.txt文件
with open(os.path.join(current_dir, 'test.txt'), 'w', encoding='utf-8') as f:
    for i in all_data[int(data_len*0.9): ]:
        text, label = i.split('\t')
        # for k, v in bianti.items():
        #     text = text.replace(k, v)
        text = convert(text, 'zh-cn').strip().replace(' ', '').replace('\n', '').replace('\r\n', '').replace(' ', '').lower()
        char_list = []
        for char in text:
            if bianti_vocab.get(char, None):
                text = text.replace(char, bianti_vocab[char])
                # text = text.replace(char, ServerConfig.bianti_vocab[char])
                char_list.append(bianti_vocab[char])
            else:
                char_list.append(char)

        text = ''.join(char_list)
        text = tokenizer.tokenize(text)
        text = ''.join(text)
        if text:
            f.write(text + '\t' + label)
