# -*- coding: utf-8 -*-
"""
@Author  : 玖月
@File    : predict_dataset_utils.py
@Date    : 2021/8/17 12:29
@Desc    : 
"""
import json
import torch

# 词表最大长度
from ml.utils.pinyin_utils import get_pinyin
from ml.utils.strokes_utils import get_strokes
from ml.utils.tokenizer import AllTokenizer

MAX_VOCAB_SIZE = 10000
# 未知字符, padding 符号
UNK, PAD = '<UNK>', 'PAD'
MIN_FREQ = 1
torch.set_num_threads(1)
tokenizer = AllTokenizer()


class LoadData(object):
    def __init__(self, config):
        self.embed_dim = config.embedding_size
        self.pad_size = config.pad_size

        self.predict_path = config.predict_data_path

        self.vocab_path = config.vocab_path
        self.vocab_pinyin_path = config.pinyin_path
        self.vocab_strokes_path = config.strokes_path
        self.char2strokes_path = config.char2strokes_path

        self.pretrain_dir = config.pretrain_dir
        self.process_embedding_dir = config.process_embedding_dir
        # self.tokenizer = lambda x: [y for y in x]  # char-level
        # self.tokenizer = lambda x: list(x)  # char-level
        self.tokenizer = lambda x: tokenizer.tokenize(x)
        self.pinyin_tokenizer = lambda x: x.split(' ')
        # self.pinyin_tokenizer = lambda x: list(x)
        self.strokes_tokenizer = lambda x: list(x)

    def load_vocab(self):
        with open(self.vocab_path, 'r') as f:
            char_vocab = json.loads(f.readlines()[0])
        with open(self.vocab_pinyin_path, 'r') as f:
            pinyin_vocab = json.loads(f.readlines()[0])
        with open(self.vocab_strokes_path, 'r') as f:
            strokes_vocab = json.loads(f.readlines()[0])
        with open(self.char2strokes_path, 'r') as f:
            char2strokes = json.loads(f.readlines()[0])
        return char_vocab, pinyin_vocab, strokes_vocab, char2strokes

    def build_batch_dataset(self, server_config, batch_data):
        raw_data, predict_data, predict_pinyin_data, predict_strokes_data = self.load_batch_dataset(
            server_config, batch_data)
        return raw_data, predict_data, predict_pinyin_data, predict_strokes_data

    def load_batch_dataset(self, server_config, batch_data):
        # config.train_path, config.pad_size
        raw_data = []
        contents = []
        pinyin_contents = []
        strokes_contents = []
        for idx, line in enumerate(batch_data):
            text = line.strip()

            text_2_vec = []  # 存放 text 转换成 id 结果
            pinyin_2_vec = []  # 存放 pinyin 转换成 id 结果
            strokes_2_vec = []  # 存放 strokes 转换成 id 结果

            token = self.tokenizer(text)
            process_text = ''.join(token)
            # print("process_text:", process_text)
            pinyin_text = get_pinyin(process_text, server_config.pinyin_tool)
            pinyin_token = self.pinyin_tokenizer(pinyin_text)
            strokes_text = get_strokes(process_text, server_config.char2strokes)
            strokes_token = self.strokes_tokenizer(strokes_text)

            raw_data.append([idx, process_text, pinyin_text, strokes_text])
            if not process_text:
                return raw_data, None, None, None

            seq_len = len(token)
            if self.pad_size:
                if len(token) < self.pad_size:
                    # 长度不够用 PAD 填充
                    token.extend([PAD] * (self.pad_size - len(token)))
                else:
                    # 长度截取
                    token = token[: self.pad_size]
                    seq_len = self.pad_size
                # 处理拼音
                if len(pinyin_token) < self.pad_size:
                    # 长度不够用 PAD 填充
                    pinyin_token.extend([PAD] * (self.pad_size - len(pinyin_token)))
                else:
                    # 长度截取
                    pinyin_token = pinyin_token[: self.pad_size]
                # 处理笔画
                if len(strokes_token) < self.pad_size:
                    # 长度不够用 PAD 填充
                    strokes_token.extend([PAD] * (self.pad_size - len(strokes_token)))
                else:
                    # 长度截取
                    strokes_token = strokes_token[: self.pad_size]

            # word 2 id
            for i in token:
                text_2_vec.append(server_config.char_vocab.get(i, server_config.char_vocab.get(UNK)))
            # pinyin 2 id
            for j in pinyin_token:
                pinyin_2_vec.append(server_config.pinyin_vocab.get(j, server_config.pinyin_vocab.get(UNK)))
            # word 2 id
            for k in strokes_token:
                strokes_2_vec.append(server_config.strokes_vocab.get(k, server_config.strokes_vocab.get(UNK)))

            contents.append((text_2_vec, int(idx), seq_len, process_text))
            pinyin_contents.append((pinyin_2_vec, int(idx), seq_len, process_text))
            strokes_contents.append((strokes_2_vec, int(idx), seq_len, process_text))
        return raw_data, contents, pinyin_contents, strokes_contents


class DatasetIterater(object):
    def __init__(self, data, pinyin_data, strokes_data, batch_size, device):
        """
        数据迭代器
        :param data: 数据集
        :param batch_size:
        :param device: gpu or cpu
        """
        # self.predict = predict
        self.batch_size = batch_size
        self.data = data
        self.pinyin_data = pinyin_data
        self.strokes_data = strokes_data

        self.n_batches = len(data) // batch_size  # batch数量
        self.device = device
        self.residue = False  # 记录 len(data)/batch 是否是整数
        # print("len(data) % self.n_batches---------------", len(data), self.n_batches, len(data) % self.n_batches)
        if self.n_batches == 0 or len(data) % self.n_batches != 0:
            # 最后一个 batch 不完整
            self.residue = True
        self.index = 0

    def _to_tensor(self, batch_data):
        # print(batch_data)
        x = torch.as_tensor([_[0] for _ in batch_data[0]])
        pinyin = torch.as_tensor([_[0] for _ in batch_data[1]])
        strokes = torch.as_tensor([_[0] for _ in batch_data[2]])
        idx = torch.as_tensor([_[1] for _ in batch_data[0]])
        seq_len = torch.as_tensor([_[2] for _ in batch_data[0]])
        return (x, pinyin, strokes, seq_len), idx

    def __next__(self):
        # print("residue and n_batches and index: ", self.residue, self.n_batches, self.index)
        if self.residue and self.index == self.n_batches:
            # 最后一个不完整 batch
            # batches = self.data[self.index * self.batch_size: ]
            batches = [self.data[self.index * self.batch_size: ],
                       self.pinyin_data[self.index * self.batch_size: ],
                       self.strokes_data[self.index * self.batch_size: ]]
            # texts = [_[3] for _ in batches]
            # print("batches=================================\n", batches)
            self.index += 1
            batches = self._to_tensor(batches)
            return batches
        elif self.index >= self.n_batches:
            self.index = 0
            raise StopIteration
        else:
            # batches = self.data[self.index * self.batch_size: (self.index+1) * self.batch_size]
            batches = [self.data[self.index * self.batch_size: (self.index + 1) * self.batch_size],
                       self.pinyin_data[self.index * self.batch_size: (self.index + 1) * self.batch_size],
                       self.strokes_data[self.index * self.batch_size: (self.index + 1) * self.batch_size]]

            self.index += 1
            batches = self._to_tensor(batches)
            return batches

    def __iter__(self):
        return self

    def __len__(self):
        if self.residue:
            return self.n_batches + 1
        else:
            return self.n_batches


def build_dataloader(data, pinyin_data, strokes_data, config):
    dataloader = DatasetIterater(data, pinyin_data, strokes_data, config.batch_size, config.device)
    return dataloader


if __name__ == "__main__":
    # read_sql_data(197, "20200826")
    pass
