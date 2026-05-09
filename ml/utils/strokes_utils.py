# -*- coding: utf-8 -*-
"""
@Author  : 玖月
@File    : strokes_utils.py
@Date    : 2021/8/6 15:15
@Desc    : 
"""
import re


def process_word(word):
    digidict = {
    '1': u'一', '2': u'二', '3': u'三', '4': u'四', '5': u'五',
    '6': u'六', '7': u'七', '8': u'八', '9': u'九', '0': u'十'
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
    word = "".join(new_word)
    return word


def get_strokes(text, char2strokes):
    text = process_word(text)
    strokes = [char2strokes.get(j) if char2strokes.get(j) else j for j in list(text)]
    strokes = ''.join(strokes)
    return strokes

# def get_strokes(text):
#     strokes_dict = {}
#     with open('processed_data/strokes.txt', 'r', encoding='utf-8') as f:
#         for i in f.readlines():
#             char, strokes = i.split(' ')
#             strokes = strokes.replace('\n', '')
#             strokes_dict[char] = strokes
#     strokes = [strokes_dict.get(j) if strokes_dict.get(j) else j for j in list(text)]
#     strokes = ''.join(strokes)
#
#     return strokes

