# -*- coding: utf-8 -*-
"""
@Author  : 玖月
@File    : TextCNN.py
@Date    : 2021/8/4 10:23
@Desc    : 
"""
import torch
import numpy as np
import torch.nn as nn
import torch.nn.functional as F
import os

torch.set_num_threads(1)


class Config(object):
    """模型参数"""

    def __init__(self, model_version='full', embedding='random'):
        """
        Parameters
        ----------
        dataset_path : 数据集根目录
        embedding : 词嵌入
        """
        dataset_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__))) + '/processed_data'
        if model_version == 'beta':
            self.model_name = 'TextCNN_Beta'
        else:
            self.model_name = 'TextCNN'
        # 数据集路径
        self.train_data_path = dataset_path + '/train.txt'
        self.dev_data_path = dataset_path + '/dev.txt'
        self.test_data_path = dataset_path + '/test.txt'
        self.train_pinyin_path = dataset_path + '/train_pinyin.txt'
        self.dev_pinyin_path = dataset_path + '/dev_pinyin.txt'
        self.test_pinyin_path = dataset_path + '/test_pinyin.txt'
        self.train_strokes_path = dataset_path + '/train_strokes.txt'
        self.dev_strokes_path = dataset_path + '/dev_strokes.txt'
        self.test_strokes_path = dataset_path + '/test_strokes.txt'

        # 各个词表路径
        self.vocab_path = dataset_path + '/vocab.json'
        self.pinyin_path = dataset_path + '/vocab_pinyin.json'
        self.strokes_path = dataset_path + '/vocab_strokes.json'
        self.char2strokes_path = dataset_path + '/char2strokes.json'

        # 词嵌入模型路径
        if embedding != 'random':
            self.embedding_pretrained = torch.tensor(np.load(dataset_path + embedding)["embeddings"].astype("float32"))
        else:
            self.embedding_pretrained = None

        # 预训练词嵌入模型路径
        self.pretrain_dir = "ml/processed_data/word_level/sgns.sogou.char"
        # 处理后的词嵌入矩阵保存路径
        self.process_embedding_dir = 'ml/processed_data/embedding_chat_contents'

        # 标签列表
        self.class_list = [x.strip() for x in open(dataset_path + '/class.txt', encoding='utf-8').readlines()]

        # 模型训练结果保存路径
        self.save_model_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__))) + '/save_dict/' + self.model_name + '.model'
        # self.save_model_path = './save_dict/' + self.model_name + '.model'

        # log 路径
        self.log_path = 'ml/log/' + self.model_name

        # 是否使用gpu或directml
        # 默认为CPU，用户可以通过命令行参数覆盖
        self.device = torch.device('cpu')
        # self.device = torch.device('cpu')

        # dropout 比例
        self.dropout = 0.8

        # 验证集 loss 超过多少batch没下降, 结束训练
        self.require_improvement = 1000

        # 标签数量
        self.num_classes = len(self.class_list)

        # 词表大小, 运行时赋值
        self.vocab_size = 0
        self.pinyin_vocab_size = 0
        self.strokes_vocab_size = 0

        # epoch 数量
        self.num_epochs = 5

        # batch 大小
        self.batch_size = 256

        # 序列长度
        self.pad_size = 64
        self.strokes_pad_size = 128
        self.pinyin_pad_size = 128

        # 学习率
        self.learning_rate = 1e-5

        # 词嵌入向量维度
        self.embedding_size = self.embedding_pretrained.size(1) if self.embedding_pretrained else 300

        # 卷积核大小，三种卷积核：2个词，3个词，4个词，维度自动匹配
        self.filter_size = (2, 3, 4) 

        # 卷积核数量
        self.num_filters = 512
        self.num_heads = 8

        # 预测数据路径
        self.predict_data_path = 'predict/predict_data_5000.csv'


# class Attention(nn.Module):
#     def __init__(self, input_dim):
#         super(Attention, self).__init__()
#         self.W = nn.Linear(input_dim, input_dim, bias=False)  # Linear layer to compute attention scores
#         self.v = nn.Linear(input_dim, 1, bias=False)  # Linear layer to compute context scores
#
#     def forward(self, x):
#         """
#         x: 输入特征, 形状为 (batch_size, seq_length, input_dim)
#         """
#         scores = self.W(x)  # Shape: (batch_size, seq_length, input_dim)
#         scores = F.tanh(scores)  # Apply tanh activation
#         attention_weights = F.softmax(self.v(scores), dim=1)  # Shape: (batch_size, seq_length, 1)
#         context = torch.bmm(attention_weights.permute(0, 2, 1), x)  # Shape: (batch_size, 1, input_dim)
#         return context.squeeze(1), attention_weights.squeeze(2)  # Shape: (batch_size, input_dim), (batch_size, seq_length)

# class Attention(nn.Module):
#     def __init__(self, input_dim):
#         super(Attention, self).__init__()
#         self.W = nn.Linear(input_dim, input_dim, bias=False)
#         self.v = nn.Linear(input_dim, 1, bias=False)
#
#     def forward(self, x):
#         scores = self.W(x)
#         scores = torch.tanh(scores)
#         attention_weights = F.softmax(self.v(scores), dim=1)
#         context = torch.bmm(attention_weights.permute(0, 2, 1), x)
#         return context.squeeze(1), attention_weights.squeeze(2)


class Model(nn.Module):
    def __init__(self, config):
        """

        Parameters
        ----------
        config : 超参数
        """
        super(Model, self).__init__()
        if config.embedding_pretrained is not None:
            # 使用预训练词向量
            # freeze = False 表示会同步训练词嵌入向量
            self.embedding = nn.Embedding.from_pretrained(config.embedding_pretrained, freeze=False)
            self.pinyin_embedding = nn.Embedding(config.pinyin_vocab_size, config.embedding_size,
                                                 padding_idx=config.pinyin_vocab_size - 1)
            self.strokes_embedding = nn.Embedding(config.strokes_vocab_size, config.embedding_size,
                                                  padding_idx=config.strokes_vocab_size - 1)
        else:
            # embedding_pretrained = torch.tensor(np.load("processed_data/embedding_chat_contents.npz")["embeddings"].astype("float32"))
            # self.embedding = nn.Embedding.from_pretrained(embedding_pretrained, freeze=False)
            self.embedding = nn.Embedding(config.vocab_size, config.embedding_size, padding_idx=config.vocab_size - 1)
            self.pinyin_embedding = nn.Embedding(config.pinyin_vocab_size, config.embedding_size,
                                                 padding_idx=config.pinyin_vocab_size - 1)
            self.strokes_embedding = nn.Embedding(config.strokes_vocab_size, config.embedding_size,
                                                  padding_idx=config.strokes_vocab_size - 1)

        self.convs = nn.ModuleList(
            [nn.Conv2d(1, config.num_filters, (k, config.embedding_size)) for k in config.filter_size]
        )

        self.pinyin_convs = nn.ModuleList(
            [nn.Conv2d(1, config.num_filters, (k, config.embedding_size)) for k in config.filter_size]
        )

        self.strokes_convs = nn.ModuleList(
            [nn.Conv2d(1, config.num_filters, (k, config.embedding_size)) for k in config.filter_size]
        )

        # Attention layer
        self.attention = nn.MultiheadAttention(embed_dim=config.num_filters * len(config.filter_size),
                                               num_heads=config.num_heads, batch_first=True)
        #
        self.dropout = nn.Dropout(config.dropout)

        self.fc = nn.Linear(config.num_filters * len(config.filter_size) * 3, config.num_classes)

    def conv_and_pool(self, x, conv):
        """
        卷积  最大池化
        Parameters
        ----------
        x :
        conv :

        Returns
        -------

        """
        x = F.relu(conv(x)).squeeze(3) #[32,512,19,1]-->[32,512,19]
        x = F.max_pool1d(x, x.size(2)).squeeze(2)#[32,512,1]-->[32,512]
        return x

    def forward(self, x):
        """
        前向传播
        Parameters
        ----------
        x :

        Returns
        -------

        """
        char = x[0]
        p = x[1]
        s = x[2]
        embed_out = self.embedding(char)
        embed_pinyin_out = self.pinyin_embedding(p)
        embed_strokes_out = self.strokes_embedding(s)

        out = embed_out.unsqueeze(1)
        pinyin_out = embed_pinyin_out.unsqueeze(1)
        strokes_out = embed_strokes_out.unsqueeze(1)

        conv_out = torch.cat([self.conv_and_pool(out, conv) for conv in self.convs], 1)
        conv_pinyin_out = torch.cat([self.conv_and_pool(pinyin_out, conv) for conv in self.pinyin_convs], 1)
        conv_strokes_out = torch.cat([self.conv_and_pool(strokes_out, conv) for conv in self.strokes_convs], 1)


        # Concatenate all conv outputs and embeddings
        # combined_features = torch.cat((conv_out, conv_pinyin_out, conv_strokes_out), dim=1)
        # combined_features = combined_features.unsqueeze(1)  # Shape: (batch_size, 1, num_features)
        # print("Combined features shape:", combined_features.shape)

        # Attention: Concatenate features and apply attention
        combined_features = torch.stack([conv_out, conv_pinyin_out, conv_strokes_out], dim=1)
        attn_out, _ = self.attention(combined_features, combined_features, combined_features)

        # Flatten, Dropout, and Fully Connected layer
        out = self.dropout(attn_out.reshape(attn_out.size(0), -1))


        # out = self.dropout(torch.cat((conv_out, conv_pinyin_out, conv_strokes_out), 1))
        # pinyin_out = self.dropout(conv_pinyin_out)
        # strokes_out = self.dropout(conv_strokes_out)

        # out = self.fc(torch.cat((out, pinyin_out, strokes_out), 1))
        out = self.fc(out)
        return out
