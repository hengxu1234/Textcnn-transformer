# -*- coding: utf-8 -*-
"""
@Author  : 玖月
@File    : predict.py
@Date    : 2021/8/4 10:22
@Desc    :
"""

import numpy as np
import pandas as pd
import torch
torch.set_num_threads(1)

from ml.utils.predict_dataset_utils import LoadData, build_dataloader


def random_seed():
    np.random.seed(1)
    torch.manual_seed(1)
    torch.cuda.manual_seed(1)
    torch.backends.cudnn.deterministic = True  # 保证每次结果都一样
    return


class Predict(object):
    @classmethod
    def predict(cls, model, dataloader, score_threshold):
        model.eval()
        predict_all = []
        with torch.no_grad():
            for step, batch in enumerate(dataloader):
                text, idx = batch
                idx = idx.cpu().tolist()
                outputs = model(text)

                predict = torch.max(outputs.data, 1)[1].cpu().tolist()
                prob = torch.softmax(outputs.data, 1).cpu().tolist()

                res_list = []
                for label, p, id in zip(predict, prob, idx):
                    # if int(p[1] * 100) >= score_threshold:
                    if p[1] >= score_threshold:
                        label_desc = 'REJECT'

                    else:
                        label_desc = 'PASS'
                    res = {
                        'label': label_desc,
                        'items': {
                                "positive_prob": p[0],
                                "negative_prob": p[1],
                        },
                        'idx': id
                    }
                    res_list.append(res)
                predict_all.extend(res_list)
        return predict_all

    @classmethod
    def run_batch(cls, server_config, batch_data, score_threshold):
        random_seed()  # 保证每次结果一致
        data = LoadData(server_config.model_config)
        raw_data, predict_data, predict_pinyin_data, predict_strokes_data = data.build_batch_dataset(server_config, batch_data)
        if not predict_data:
            return [{
                "id": 0,
                "items": {
                    "negative_prob": 0,
                    "positive_prob": 1
                },
                "label": "PASS",
                "pinyin": "",
                "strokes": "",
                "text": ""
            }]
        splice_contents = []
        for _, t, p, s in raw_data[:2]:
            text = str(t) + str(p) + str(s)
            if text:
                splice_contents.append(str(t) + str(p) + str(s))

        # 使用自定义的 dataloader
        print(server_config.model_config.device, 'server_config.model_config')

        pre_dataloader = build_dataloader(predict_data, predict_pinyin_data, predict_strokes_data, server_config.model_config)

        # 实例化 Model 类, 并加载训练好的模型
        predict_all = cls.predict(server_config.prepare_model, pre_dataloader, score_threshold)

        for i in predict_all:
            idx = i['idx']
            raw_data[idx].extend([i['label'], i['items']])

        raw_data = pd.DataFrame(raw_data)
        raw_data.columns = ['id', 'text', 'pinyin', 'strokes', 'label', 'items']
        res_data = raw_data.to_dict(orient='records')
        return res_data


if __name__ == "__main__":
    text = '1111122222'

    from app.config.setting import ServerConfig

    from zhconv import convert
    from ml.utils.bianti_vocab_map import escape_map as bianti_vocab
    from ml.utils.tokenizer import AllTokenizer
    text = convert(text, 'zh-cn').strip().replace(' ', '').replace('\n', '').replace('\r\n', '').replace(' ', '').lower()
    # for char in text:
    #     if bianti_vocab.get(char, None):
    #         text = text.replace(char, bianti_vocab[char])
    char_list = []
    for char in text:
        if bianti_vocab.get(char, None):
            text = text.replace(char, bianti_vocab[char])
            char_list.append(bianti_vocab[char])
        else:
            char_list.append(char)

    text = ''.join(char_list)
    print(text, 'before tokenizer')

    tokenizer = AllTokenizer()
    text = tokenizer.tokenize(text)
    print(text, 'tokenizer')
    text = ''.join(text)
    text = text.lower()
    print(text, text.lower(), 'text111')
    batch_data = [text]

    res = Predict.run_batch(ServerConfig, batch_data, 0.8)
    print(res)

