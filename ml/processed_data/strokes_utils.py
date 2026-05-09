# -*- coding: utf-8 -*-
"""
@Author  : 玖月
@File    : strokes_utils.py
@Date    : 2021/8/6 15:15
@Desc    : 
"""
import re
import os

# 获取当前文件所在目录的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))

strokes_dict = {}
strokes_set = []

# 使用绝对路径读取 strokes.txt
with open(os.path.join(current_dir, 'strokes.txt'), 'r', encoding='utf-8') as f:
    for i in f.readlines():
        char, strokes = i.split(' ')
        strokes = strokes.replace('\n', '')
        strokes_dict[char] = strokes
        if '\n' in list(strokes):
            print(char, strokes)
        strokes_set.extend(list(strokes))

print(len(strokes_dict))

# print("="*50)
# print(len(strokes_set))
#
# strokes_set = list(set(strokes_set))
#
# print(strokes_set)
# set_dict = {k: v for v, k in enumerate(strokes_set)}
# set_dict['<unk>'] = 25
# print(set_dict)
#
# process_strokes_dict = {}
# for k, v in strokes_dict.items():
#     num_list = []
#     for i in list(v):
#         num_list.append(set_dict[i] if set_dict.get(i) else set_dict.get('<unk>'))
#     print(num_list)
#     # num = ''.join(num_list)
#
#     process_strokes_dict[k] = num_list
#
# print(len(process_strokes_dict))
# print(list(process_strokes_dict.values())[:10])


def process_word(word):
    digidict = {
    '1': u'一', '2': u'二', '3': u'三', '4': u'四', '5': u'五',
    '6': u'六', '7': u'七', '8': u'八', '9': u'九', '0': u'零'
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


# 使用绝对路径读取和写入文件
with open(os.path.join(current_dir, 'train.txt'), 'r', encoding='utf-8') as f:
    with open(os.path.join(current_dir, 'train_strokes.txt'), 'w', encoding='utf-8') as sf:
        for i in f.readlines():
            # print(i)
            text, label = i.split('\t')
            text = process_word(text)
            strokes = [strokes_dict.get(j) if strokes_dict.get(j) else j for j in list(text)]
            strokes = ''.join(strokes)

            sf.write(strokes + '\t' + label)


with open(os.path.join(current_dir, 'dev.txt'), 'r', encoding='utf-8') as f:
    with open(os.path.join(current_dir, 'dev_strokes.txt'), 'w', encoding='utf-8') as sf:
        for i in f.readlines():
            # print(i)
            text, label = i.split('\t')
            text = process_word(text)
            strokes = [strokes_dict.get(j) if strokes_dict.get(j) else j for j in list(text)]
            strokes = ''.join(strokes)

            sf.write(strokes + '\t' + label)


with open(os.path.join(current_dir, 'test.txt'), 'r', encoding='utf-8') as f:
    with open(os.path.join(current_dir, 'test_strokes.txt'), 'w', encoding='utf-8') as sf:
        for i in f.readlines():
            # print(i)
            text, label = i.split('\t')
            text = process_word(text)
            strokes = [strokes_dict.get(j) if strokes_dict.get(j) else j for j in list(text)]
            strokes = ''.join(strokes)

            sf.write(strokes + '\t' + label)