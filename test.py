# -*- coding: utf-8 -*-
"""
@Author  : 玖月
@File    : test.py
@Date    : 2021/8/27 15:18
@Desc    : 
"""
import pandas as pd
import numpy as np

company=["A","B","C"]

data=pd.DataFrame({
    "company": [company[x] for x in np.random.randint(0,len(company),10)],
    "salary": np.random.randint(5, 50, 10),
    "age": np.random.randint(15, 50, 10)
}
)

print(data)
def keyword_count(keywords, topK=10):
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

    tags = sorted(freq, key=freq.__getitem__, reverse=True)
    if topK:
        return tags[:topK]
    else:
        return tags

group_data = data.groupby('company')
print(group_data)
for i in group_data:
    print(i[0], list(i[1]['salary']))