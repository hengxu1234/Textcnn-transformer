# -*- coding: utf-8 -*-
"""
@Author  : 玖月
@File    : keyword_utils.py
@Date    : 2021/8/27 12:01
@Desc    : 
"""
import datetime
import re
from operator import itemgetter

from jieba_fast import analyse
import pandas as pd


tfidf = analyse.extract_tags  # 基于TF-IDF算法提取句子的关键字



def clear_emtion_char(sentence):
    pattern2 = re.compile(r'\{[0-9]+\}')
    pattern3 = re.compile(r'#<E:[0-9]+>#')
    pattern4 = re.compile(r'\*[0-9]+\.png')
    pattern5 = re.compile(r'@[0-9]+')
    pattern6 = re.compile(r'\[(.*?)\]')
    sentence = re.sub(pattern6, '', sentence)
    sentence = re.sub(pattern2, '', sentence)
    sentence = re.sub(pattern3, '', sentence)
    sentence = re.sub(pattern4, '', sentence)
    sentence = re.sub(pattern5, '', sentence)
    return sentence


def extract_tags(text):
    if not text.strip():
        return ''
    tf_key = tfidf(clear_emtion_char(text))
    # tr_key = textrank(text)
    result = "|".join(tf_key[:5])
    return result


def _count(keywords, topK=10, withWeight=True):
    kw_list = []
    for i in keywords:
        if i:
            kw_list.extend(i.split('|'))

    freq = {}
    for w in kw_list:
        if not w:
            continue
        if len(w.strip()) < 2:
            continue
        freq[w] = freq.get(w, 0) + 1

    if withWeight:
        tags = sorted(freq.items(), key=itemgetter(1), reverse=True)
    else:
        tags = sorted(freq, key=freq.__getitem__, reverse=True)

    if topK:
        return tags[:topK]
    else:
        return tags


def keyword_count(df_data, ds):
    date1 = datetime.datetime.strptime(ds, "%Y%m%d%H%M")
    # print(date1, date1.timestamp(), (date1 + datetime.timedelta(hours=-1)).timestamp())
    # 转换成时间戳
    end_time = int(date1.timestamp())
    start_time = int((date1 + datetime.timedelta(minutes=-5)).timestamp())

    df_data = df_data[df_data['pred_risk_level'] != 'PASS']
    group_data = df_data[['game_id', 'keywords']].groupby('game_id')
    # print(df_data[['game_id', 'keywords']])
    # print(list(group_data))
    count_res = []
    for game_id, df in group_data:
        keyword_count = _count(df['keywords'])
        # print(keyword_count)
        for k, count in keyword_count:
            count_res.append([start_time, end_time, count, k, game_id])

    df_res = pd.DataFrame(count_res)
    # print(df_res)
    df_res.columns = ['start_time', 'end_time', 'count', 'keyword', 'game_id']
    return df_res
