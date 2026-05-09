# -*- coding: utf-8 -*-
"""
@Author  : 玖月
@File    : dataset_utils.py
@Date    : 2021/8/4 19:30
@Desc    : 
"""
import json
import os

import torch
from torch.utils.data.dataset import Dataset
import numpy as np
from tqdm import tqdm

from ml.utils.tokenizer import AllTokenizer

# 获取当前文件所在目录的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取 processed_data 目录的绝对路径
processed_data_dir = os.path.join(os.path.dirname(current_dir), 'processed_data')

# 词表最大长度
MAX_VOCAB_SIZE = 10000
# 未知字符, padding 符号
UNK, PAD = '<UNK>', 'PAD'
# 目录、文件名按需更改。
TRAIN_PATH = os.path.join(processed_data_dir, 'train.txt')
DEV_PATH = os.path.join(processed_data_dir, 'dev.txt')
TEST_PATH = os.path.join(processed_data_dir, 'test.txt')
VOCAB_PATH = os.path.join(processed_data_dir, 'vocab.json')

TRAIN_PINYIN_PATH = os.path.join(processed_data_dir, 'train_pinyin.txt')
DEV_PINYIN_PATH = os.path.join(processed_data_dir, 'dev_pinyin.txt')
TEST_PINYIN_PATH = os.path.join(processed_data_dir, 'test_pinyin.txt')
VOCAB_PINYIN_PATH = os.path.join(processed_data_dir, 'vocab_pinyin.json')

TRAIN_STROKES_PATH = os.path.join(processed_data_dir, 'train_strokes.txt')
DEV_STROKES_PATH = os.path.join(processed_data_dir, 'dev_strokes.txt')
TEST_STROKES_PATH = os.path.join(processed_data_dir, 'test_strokes.txt')
VOCAB_STROKES_PATH = os.path.join(processed_data_dir, 'vocab_strokes.json')

MIN_FREQ = 1
PAD_SIZE = 32
PAD_STROKES_SIZE = 128
PAD_PINYIN_SIZE = 128

# 预训练词嵌入模型路径
PRETRAIN_DIR = os.path.join(processed_data_dir, 'sgns.sogou.char')
# 词嵌入模型维度
EMBED_DIM = 300
# 处理后的词嵌入矩阵保存路径
PROCESS_EMBEDDING_DIR = os.path.join(processed_data_dir, 'embedding_chat_contents')
tokenizer = AllTokenizer()


class LoadData(object):
    def __init__(self):
        self.embed_dim = EMBED_DIM
        self.pad_size = PAD_SIZE
        self.pad_strokes_size = PAD_STROKES_SIZE
        self.pad_pinyin_size = PAD_PINYIN_SIZE
        self.train_path = TRAIN_PATH
        self.dev_path = DEV_PATH
        self.test_path = TEST_PATH
        self.vocab_path = VOCAB_PATH

        self.train_pinyin_path = TRAIN_PINYIN_PATH
        self.dev_pinyin_path = DEV_PINYIN_PATH
        self.test_pinyin_path = TEST_PINYIN_PATH
        self.vocab_pinyin_path = VOCAB_PINYIN_PATH

        self.train_strokes_path = TRAIN_STROKES_PATH
        self.dev_strokes_path = DEV_STROKES_PATH
        self.test_strokes_path = TEST_STROKES_PATH
        self.vocab_strokes_path = VOCAB_STROKES_PATH

        self.pretrain_dir = PRETRAIN_DIR
        self.process_embedding_dir = PROCESS_EMBEDDING_DIR
        # self.tokenizer = lambda x: [y for y in x]  # char-level
        self.tokenizer = lambda x: tokenizer.tokenize(x)  # char-level
        self.pinyin_tokenizer = lambda x: x.split(' ')
        # self.pinyin_tokenizer = lambda x: list(x)
        self.strokes_tokenizer = lambda x: list(x)

    def build_vocab(self):
        """
        创建词表
        :return: vocab_dic -> dict
        """
        vocab_dic = {}
        pinyin_vocab_dict = {}
        strokes_vocab_dict = {}

        with open(self.train_path, 'r', encoding='utf-8') as f:
            for line in tqdm(f.readlines()):
                line = line.strip()
                if not line:
                    continue
                text = line.split('\t')[0]
                for word in self.tokenizer(text):
                    vocab_dic[word] = vocab_dic.get(word, 0) + 1
            vocab_list = sorted([_ for _ in vocab_dic.items() if _[1] >= MIN_FREQ],
                                key=lambda x: x[1], reverse=True)[: MAX_VOCAB_SIZE]
            # vocab_list: [('你', 4870), ('我', 4335), ('的', 2475), ('不', 2331), ('是', 2170), ('了', 1980)...]
            vocab_dic = {word_count[0]: idx for idx, word_count in enumerate(vocab_list)}
            # vocab_dic: {'你': 0, '我': 1, '的': 2, '不': 3, '是': 4, '了': 5, '一': 6, '好': 7, ...}
            vocab_dic.update({UNK: len(vocab_dic), PAD: len(vocab_dic) + 1})

        with open(self.train_pinyin_path, 'r', encoding='utf-8') as f:
            for line in tqdm(f.readlines()):
                line = line.strip()
                if not line:
                    continue
                text = line.split('\t')[0]
                for word in self.pinyin_tokenizer(text):
                    pinyin_vocab_dict[word] = pinyin_vocab_dict.get(word, 0) + 1
            pinyin_vocab_list = sorted([_ for _ in pinyin_vocab_dict.items() if _[1] >= MIN_FREQ],
                                key=lambda x: x[1], reverse=True)[: MAX_VOCAB_SIZE]
            # vocab_list: [('你', 4870), ('我', 4335), ('的', 2475), ('不', 2331), ('是', 2170), ('了', 1980)...]
            pinyin_vocab_dict = {word_count[0]: idx for idx, word_count in enumerate(pinyin_vocab_list)}
            # vocab_dic: {'你': 0, '我': 1, '的': 2, '不': 3, '是': 4, '了': 5, '一': 6, '好': 7, ...}
            pinyin_vocab_dict.update({UNK: len(pinyin_vocab_dict), PAD: len(pinyin_vocab_dict) + 1})

        with open(self.train_strokes_path, 'r', encoding='utf-8') as f:
            for line in tqdm(f.readlines()):
                line = line.strip()
                if not line:
                    continue
                text = line.split('\t')[0]
                for word in self.strokes_tokenizer(text):
                    strokes_vocab_dict[word] = strokes_vocab_dict.get(word, 0) + 1
            strokes_vocab_list = sorted([_ for _ in strokes_vocab_dict.items() if _[1] >= MIN_FREQ],
                                key=lambda x: x[1], reverse=True)[: MAX_VOCAB_SIZE]
            # vocab_list: [('你', 4870), ('我', 4335), ('的', 2475), ('不', 2331), ('是', 2170), ('了', 1980)...]
            strokes_vocab_dict = {word_count[0]: idx for idx, word_count in enumerate(strokes_vocab_list)}
            # vocab_dic: {'你': 0, '我': 1, '的': 2, '不': 3, '是': 4, '了': 5, '一': 6, '好': 7, ...}
            strokes_vocab_dict.update({UNK: len(strokes_vocab_dict), PAD: len(strokes_vocab_dict) + 1})
        return vocab_dic, pinyin_vocab_dict, strokes_vocab_dict

    def build_dataset(self):
        # if os.path.exists(self.vocab_path) and os.path.exists(self.vocab_pinyin_path) and \
        #         os.path.exists(self.vocab_strokes_path):
        #     # 如果词表已存在, 直接加载
        #     with open(self.vocab_path, 'r') as f:
        #         vocab = json.loads(f.readlines()[0])
        #     with open(self.vocab_pinyin_path, 'r') as f:
        #         pinyin_vocab = json.loads(f.readlines()[0])
        #     with open(self.vocab_strokes_path, 'r') as f:
        #         strokes_vocab = json.loads(f.readlines()[0])
        # else:
        vocab, pinyin_vocab, strokes_vocab = self.build_vocab()
        # 保存文件
        with open(self.vocab_path, 'w') as f:
            f.write(json.dumps(vocab))
        with open(self.vocab_pinyin_path, 'w') as f:
            f.write(json.dumps(pinyin_vocab))
        with open(self.vocab_strokes_path, 'w') as f:
            f.write(json.dumps(strokes_vocab))

        print(f"Vocab size(词表大小): {len(vocab)}")
        print(f"Pinyin Vocab size(词表大小): {len(pinyin_vocab)}")
        print(f"Strokes Vocab size(词表大小): {len(strokes_vocab)}")
        # 限制训练数据为20000条
        max_train_samples = 20000
        train_data = self.load_dataset(self.train_path, vocab, tokenizer='char', max_samples=max_train_samples)
        dev_data = self.load_dataset(self.dev_path, vocab, tokenizer='char')
        test_data = self.load_dataset(self.test_path, vocab, tokenizer='char')

        train_pinyin_data = self.load_dataset(self.train_pinyin_path, pinyin_vocab, tokenizer='pinyin', max_samples=max_train_samples)
        dev_pinyin_data = self.load_dataset(self.dev_pinyin_path, pinyin_vocab, tokenizer='pinyin')
        test_pinyin_data = self.load_dataset(self.test_pinyin_path, pinyin_vocab, tokenizer='pinyin')

        train_strokes_data = self.load_dataset(self.train_strokes_path, strokes_vocab, tokenizer='strokes', max_samples=max_train_samples)
        dev_strokes_data = self.load_dataset(self.dev_strokes_path, strokes_vocab, tokenizer='strokes')
        test_strokes_data = self.load_dataset(self.test_strokes_path, strokes_vocab, tokenizer='strokes')
        return vocab, pinyin_vocab, strokes_vocab, train_data, dev_data, test_data, train_pinyin_data, \
                        dev_pinyin_data, test_pinyin_data, train_strokes_data, dev_strokes_data, test_strokes_data

    def load_dataset(self, file_path, vocab, tokenizer, max_samples=None):
        """
        加载数据
        :param file_path:
        :param max_samples: 最大样本数
        :return:
        """
        # config.train_path, config.pad_size
        contents = []
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if max_samples:
                lines = lines[:max_samples]
            for line in tqdm(lines):
                line = line.strip()
                # print(line)
                if not line:
                    continue
                text, label = line.split('\t')
                text_2_vec = []  # 存放 text 转换成 id 结果

                if tokenizer == 'char':
                    token = self.tokenizer(text)
                    # print(token)
                    seq_len = len(token)
                    if len(token) < self.pad_size:
                        # 长度不够用 PAD 填充
                        token.extend([PAD] * (self.pad_size - len(token)))
                    else:
                        # 长度截取
                        token = token[: self.pad_size]
                        seq_len = self.pad_size
                elif tokenizer == 'pinyin':
                    token = self.pinyin_tokenizer(text)
                    # print(token)
                    seq_len = len(token)
                    if len(token) < self.pad_pinyin_size:
                        # 长度不够用 PAD 填充
                        token.extend([PAD] * (self.pad_pinyin_size - len(token)))
                    else:
                        # 长度截取
                        token = token[: self.pad_pinyin_size]
                        seq_len = self.pad_pinyin_size
                else:
                    token = self.strokes_tokenizer(text)
                    # print(token)
                    seq_len = len(token)
                    if len(token) < self.pad_strokes_size:
                        # 长度不够用 PAD 填充
                        token.extend([PAD] * (self.pad_strokes_size - len(token)))
                    else:
                        # 长度截取
                        token = token[: self.pad_strokes_size]
                        seq_len = self.pad_strokes_size

                # if self.pad_size:
                #     if len(token) < self.pad_size:
                #         # 长度不够用 PAD 填充
                #         token.extend([PAD] * (self.pad_size - len(token)))
                #     else:
                #         # 长度截取
                #         token = token[: self.pad_size]
                #         seq_len = self.pad_size
                # word 2 id
                for i in token:
                    text_2_vec.append(vocab.get(i, vocab.get(UNK)))
                contents.append((text_2_vec, int(label), seq_len, text))
        return contents


def build_pre_embedding_file():
    '''提取预训练词向量'''
    vocab_path = VOCAB_PATH
    process_embedding_dir = PROCESS_EMBEDDING_DIR
    pretrain_dir = PRETRAIN_DIR

    if os.path.exists(process_embedding_dir + ".npz"):
        print("已检测到提取过的预训练词向量文件: ", process_embedding_dir + ".npz")
        return
    else:
        print("提取预训练词向量中...")
        if os.path.exists(vocab_path):
            with open(vocab_path, 'r') as f:
                vocab_dict = json.loads(f.readlines()[0])
        else:
            loaddata = LoadData()
            vocab_dict = loaddata.build_vocab()
            with open(vocab_path, 'w') as f:
                f.write(json.dumps(vocab_dict))

        embeddings = np.random.rand(len(vocab_dict), EMBED_DIM)
        with open(pretrain_dir, "r", encoding='utf-8') as f:
            for line in f.readlines()[1:]:  # 第一行是标题, 跳过
                line = line.strip().split(" ")
                if line[0] in vocab_dict:
                    idx = vocab_dict[line[0]]
                    embed = [float(x) for x in line[1: ]]
                    embeddings[idx] = np.asarray(embed, dtype="float32")
        np.savez_compressed(process_embedding_dir, embeddings=embeddings)
        print("预训练词向量提取完成, 且保存成功: ", process_embedding_dir + ".npz")


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
        if len(data) % self.n_batches != 0:
            # 最后一个 batch 不完整
            self.residue = True
        self.index = 0

    def _to_tensor(self, batch_data):
        # print(self.device)
        # x = torch.LongTensor([_[0] for _ in batch_data[0]]).to(self.device)
        # pinyin = torch.LongTensor([_[0] for _ in batch_data[1]]).to(self.device)
        # strokes = torch.LongTensor([_[0] for _ in batch_data[2]]).to(self.device)
        # y = torch.LongTensor([_[1] for _ in batch_data[0]]).to(self.device)
        # seq_len = torch.LongTensor([_[2] for _ in batch_data[0]]).to(self.device)
        x = torch.as_tensor([_[0] for _ in batch_data[0]]).to(self.device)
        pinyin = torch.as_tensor([_[0] for _ in batch_data[1]]).to(self.device)
        strokes = torch.as_tensor([_[0] for _ in batch_data[2]]).to(self.device)
        y = torch.as_tensor([_[1] for _ in batch_data[0]]).to(self.device)
        seq_len = torch.as_tensor([_[2] for _ in batch_data[0]]).to(self.device)
        return (x, pinyin, strokes, seq_len), y

    def __next__(self):
        if self.residue and self.index == self.n_batches:
            # 最后一个不完整 batch
            batches = [self.data[self.index * self.batch_size: ],
                       self.pinyin_data[self.index * self.batch_size: ],
                       self.strokes_data[self.index * self.batch_size: ]]
            texts = [_[3] for _ in batches[0]]
            self.index += 1
            batches = self._to_tensor(batches)
            return batches
        elif self.index >= self.n_batches:
            self.index = 0
            raise StopIteration
        else:
            batches = [self.data[self.index * self.batch_size: (self.index+1) * self.batch_size],
                       self.pinyin_data[self.index * self.batch_size: (self.index+1) * self.batch_size],
                       self.strokes_data[self.index * self.batch_size: (self.index+1) * self.batch_size], ]
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
    # (text_2_vec, int(label), seq_len, text)
    dataloader = DatasetIterater(data, pinyin_data, strokes_data, config.batch_size, config.device)
    return dataloader


def num_examples(dataloader) -> int:
    """
    Helper to get number of samples in a :class:`~torch.utils.data.DataLoader` by accessing its dataset.
    """
    return len(dataloader.dataset)


if __name__ == "__main__":
    data = LoadData(use_word=False)
    data.build_pre_embedding_file()
    # vocab, train_data, dev_data, test_data = data.build_dataset()
    # train_dataset = BuildDataSet(train_data)
    # train_dataloader = DataLoader(dataset=train_dataset, batch_size=128, shuffle=True)
    # print("233")
