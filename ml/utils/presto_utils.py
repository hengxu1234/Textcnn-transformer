# -*- coding: utf-8 -*-
"""
@Author  : 玖月
@File    : presto_utils.py
@Date    : 2021/8/20 15:12
@Desc    : 
"""
import json
import time
import hashlib

import requests
from tqdm import tqdm


def str2md5(str):
    m = hashlib.md5()
    m.update(str.encode('utf-8'))
    return m.hexdigest()


def get_task_id(sql, **kwargs):
    # 封装 MD5 请求 sign
    timestamp = int(time.time())
    api_params = '''{"sql":"%s","query_priority":%d}''' % (sql, 15)
    md5_str = '_key=%s&api_name=%s&api_params=%s&client_id=%s&timestamp=%s' % (
        kwargs['key'], kwargs['api_name'], api_params, kwargs['client_id'], timestamp)
    sign = str2md5(md5_str)

    # 请求 api
    json_params = {
        'client_id': kwargs['client_id'],
        'api_name': kwargs['api_name'],
        'api_params': api_params,
        'timestamp': timestamp,
        'sign': sign
    }
    res = requests.post(kwargs['data_api_url'], json=json_params).text
    res = json.loads(res)

    # 获得task_id
    task_id = res['data']['task_id']
    return task_id


def get_job_status(task_id, **kwargs):
    """
    获取查询任务执行状态
    Returns:

    """
    flag = 1
    start_time = 0

    api_params = '''{'serial_no':'%s'}''' % task_id

    while start_time < 80000 and flag:
        timestamp = int(time.time())
        md5_str = '_key=%s&api_name=get_task&api_params=%s&client_id=%s&timestamp=%s' % (
            kwargs['key'], api_params, kwargs['client_id'], timestamp)
        sign = str2md5(md5_str)
        json_params = {'client_id': kwargs['client_id'], 'api_name': 'get_task', 'api_params': api_params,
                      'timestamp': timestamp, 'sign': sign}

        res = requests.post(kwargs['data_api_url'], json=json_params).text
        res = json.loads(res)

        job_status = res['data']['jobs']['status']

        if job_status == '成功':
            flag = 0
            total = res['data']['jobs']['total']
            print('query data total: {}'.format(total))
        elif job_status == '失败':
            print('get job status failed!')
            total = -1
            break
    return total


def get_data(sql, type):
    """
    通过 data api 接口请求 presto/hive 数据
    Args:
        sql: sql 语句
        type: 查询类型 hive or presto

    Returns:

    """
    presto_name = 'pmc_mining_data_query'
    hive_name = 'hive_pmc_mining_data_query'
    kwargs = dict(
        client_id=61,
        key='6e52ed66c2403ceb03a87ad3c5887e71',
        api_name=hive_name if type == 'hive' else presto_name,
        data_api_url='http://data-api.dc.uuzu.com/search/'
    )
    task_id = get_task_id(sql, **kwargs)
    print(task_id)
    
    total = get_job_status(task_id, **kwargs)

    # 分页获取数据
    batch_size = 20000
    n_batches = total // batch_size
    start = 1

    all_data = []
    for i in tqdm(range(n_batches+1), desc='分页获取数据中...'):
        api_params = '''{'task_id': '%s','from': %d,'size': %d}''' % (task_id, start, batch_size)
        timestamp = int(time.time())
        start += batch_size
        md5_str = '_key=%s&api_name=%s&api_params=%s&client_id=%s&timestamp=%s' % (
            kwargs['key'], kwargs['api_name'], api_params, kwargs['client_id'], timestamp)
        sign = str2md5(md5_str)

        json_params = {'client_id': kwargs['client_id'], 'api_name': kwargs['api_name'], 'api_params': api_params,
                       'timestamp': timestamp, 'sign': sign}

        batch_res = requests.post(kwargs['data_api_url'], json=json_params).text
        batch_res = json.loads(batch_res)

        batch_data = batch_res['data'].get('result', '')
        if not batch_data:
            print('分页查询数据出错, 当前页数: {}, 查询接口返回结果: \n{}'.format(i+1, batch_res))
        else:
            all_data.extend(batch_data)

    print("分页查询所有数据完成...\ntotal 数量: {}, 获取数据总量: {}".format(total, len(all_data)))
    return all_data


if __name__ == '__main__':
    sql = """
    select 
        request_id, response_id, timestamp, token_id, role_name, text, gameid, server_id, account_id, role_id, channel, risk_level
    from 
        pri_ml_dept_txt.bdl_game_chat_public_opinion 
    where 
        game_id = '360'
    and
        ds = '20210823'
    limit 100
    """
    all_data = get_data(sql, "presto")
    for i in all_data[:10]:
        print(i)
