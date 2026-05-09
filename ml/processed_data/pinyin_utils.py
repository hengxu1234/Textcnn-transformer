# -*- coding: utf-8 -*-
"""
@Author  : 玖月
@File    : pinyin_utils.py
@Date    : 2021/8/6 16:37
@Desc    : 
"""
import re
import os

from xpinyin import Pinyin

# 获取当前文件所在目录的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))

p = Pinyin()


def process_word(word):
    digidict = {
    '1': u'yi', '2': u'er', '3': u'san', '4': u'si', '5': u'wu',
    '6': u'liu', '7': u'qi', '8': u'ba', '9': u'jiu', '0': u'ling'
    }

    patten = '([0-9]{1})'
    new_word = []
    for i in word:
        if re.search(patten, i):
            py = digidict[i]
            new_word.append(py)
        elif i.strip():
            # print(i)
            new_word.append(i.strip())
    word = " ".join(new_word)
    return word

# print(process_word("nihk 你好...123哈哈"))
# print(p.get_pinyin(process_word("nihk 你好...123哈哈"), ''))


def get_pinyin(word):
    py = [p.get_pinyin(process_word(j), '') for j in list(word)]
    py = ' '.join(py)
    return py


# 使用绝对路径读取和写入文件
with open(os.path.join(current_dir, 'train.txt'), 'r', encoding='utf-8') as f:
    with open(os.path.join(current_dir, 'train_pinyin.txt'), 'w', encoding='utf-8') as pf:
        for i in f.readlines():
            print(i)
            text, label = i.split('\t')
            py = [p.get_pinyin(process_word(j), '') for j in list(text)]
            # print(py)
            py = ' '.join(py)
            pf.write(py + '\t' + label)

with open(os.path.join(current_dir, 'dev.txt'), 'r', encoding='utf-8') as f:
    with open(os.path.join(current_dir, 'dev_pinyin.txt'), 'w', encoding='utf-8') as pf:
        for i in f.readlines():
            print(i)
            text, label = i.split('\t')
            py = [p.get_pinyin(process_word(j), '') for j in list(text)]
            # print(py)
            py = ' '.join(py)
            pf.write(py + '\t' + label)


with open(os.path.join(current_dir, 'test.txt'), 'r', encoding='utf-8') as f:
    with open(os.path.join(current_dir, 'test_pinyin.txt'), 'w', encoding='utf-8') as pf:
        for i in f.readlines():
            print(i)
            text, label = i.split('\t')
            py = [p.get_pinyin(process_word(j), '') for j in list(text)]
            # print(py)
            py = ' '.join(py)
            pf.write(py + '\t' + label)


if __name__ == "__main__":
    # print(process_word("nihk 你好...123哈哈"))
    # print(p.get_pinyin(process_word("nihk 你好...123哈哈"), ''))
    pass
