# -*- coding: utf-8 -*-
"""
@Author  : 玖月
@File    : pinyin_utils.py
@Date    : 2021/8/6 16:37
@Desc    : 
"""
import re

from xpinyin import Pinyin

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


def get_pinyin(word, p):
    py = [p.get_pinyin(process_word(j), '') for j in list(word)]
    py = ' '.join(py)
    return py


if __name__ == "__main__":
    print(process_word('123'))
    # print(get_pinyin('123'))
