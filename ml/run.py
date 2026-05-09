# -*- coding: utf-8 -*-
"""
@Author  : 玖月
@File    : run.py
@Date    : 2021/8/4 19:28
@Desc    : 
"""
import argparse
import time
from importlib import import_module

import numpy as np
import torch
import os

from train import init_network, train
from ml.utils.time_utils import get_time_dif
from ml.utils.dataset_utils import build_pre_embedding_file
from ml.utils.dataset_utils import LoadData, build_dataloader


def run(args):

    if args.embedding == 'random':

        embedding = "random"
    else:
        # 使用词嵌入
        embedding = 'embedding_chat_contents.npz'
        build_pre_embedding_file()

    model_name = args.model

    # import model
    model = import_module('model.' + model_name)
    config = model.Config(embedding)
    
    # 根据命令行参数设置设备
    if args.device == 'dml':
        try:
            import torch_directml
            config.device = torch_directml.device()
            print('Using DirectML device:', config.device)
            # 测试设备是否能正常工作
            test_tensor = torch.tensor([1.0], device=config.device)
            test_tensor.to(config.device)
        except (ImportError, RuntimeError):
            print('DirectML not available or failed, falling back to CPU')
            config.device = torch.device('cpu')
    elif args.device == 'cuda' and torch.cuda.is_available():
        config.device = torch.device('cuda:0')
        print('Using CUDA device:', config.device)
    else:
        config.device = torch.device('cpu')
        print('Using CPU device:', config.device)


    np.random.seed(1)
    torch.manual_seed(1)
    torch.cuda.manual_seed(1)
    torch.backends.cudnn.deterministic = True  # 保证每次结果都一样

    start_time = time.time()
    print("Loading data...")
    data = LoadData()

    # vocab, train_data, dev_data, test_data = data.build_dataset()
    vocab, pinyin_vocab, strokes_vocab, train_data, dev_data, test_data, train_pinyin_data, \
    dev_pinyin_data, test_pinyin_data, train_strokes_data, dev_strokes_data, test_strokes_data = data.build_dataset()

    # 使用自定义的 dataloader
    train_dataloader = build_dataloader(train_data, train_pinyin_data, train_strokes_data, config)
    dev_dataloader = build_dataloader(dev_data, dev_pinyin_data, dev_strokes_data, config)
    test_dataloader = build_dataloader(test_data, test_pinyin_data, test_strokes_data, config)

    time_dif = get_time_dif(start_time)
    print("Time usage: ", time_dif)

    # train
    config.vocab_size = len(vocab)
    config.pinyin_vocab_size = len(pinyin_vocab)
    config.strokes_vocab_size = len(strokes_vocab)

    # 实例化 Model 类
    model = model.Model(config).to(config.device)
    if model_name != "transformer":
        init_network(model)
    print(model.parameters)
    train(config, model, train_dataloader, dev_dataloader, test_dataloader)


# def run_online(model, embedding, focal_loss, word):
#     dataset = "processed_data"  # 处理过数据集根目录
#     if embedding == 'random':
#         embedding = "random"
#     else:
#         # 使用词嵌入
#         embedding = 'embedding_chat_contents.npz'
#         build_pre_embedding_file()
#
#     model_name = model
#     if model_name == 'FastText':
#         from utils.dataset_utils_fasttext import LoadData, build_dataloader
#         embedding = 'random'
#     else:
#         from utils.dataset_utils import LoadData, build_dataloader
#
#     # import model
#     model = import_module('model.' + model_name)
#     config = model.Config(dataset, embedding)
#
#     np.random.seed(1)
#     torch.manual_seed(1)
#     torch.cuda.manual_seed(1)
#     torch.backends.cudnn.deterministic = True  # 保证每次结果都一样
#
#     start_time = time.time()
#     print("Loading data...")
#     data = LoadData()
#
#     vocab, train_data, dev_data, test_data = data.build_dataset()
#
#     # 使用自定义的 dataloader
#     train_dataloader = build_dataloader(train_data, config)
#     dev_dataloader = build_dataloader(dev_data, config)
#     test_dataloader = build_dataloader(test_data, config)
#
#     time_dif = get_time_dif(start_time)
#     print("Time usage: ", time_dif)
#
#     # train
#     config.vocab_size = len(vocab)
#     # 实例化 Model 类
#     model = model.Model(config).to(config.device)
#     if model_name != "transformer":
#         init_network(model)

#     print(model.parameters)
#     test_res = train(config, model, train_dataloader, dev_dataloader, test_dataloader)
#     return test_res


if __name__ == "__main__":
    # gpu 使用多进程需要下面配置
    # torch.multiprocessing.set_start_method('spawn')
    parser = argparse.ArgumentParser(description="Chat Sentiment Analysis")
    parser.add_argument('--model', default='TextCNN', type=str, help="choose a model: TextRNN")
    parser.add_argument('--embedding', default='random', type=str, help="random or pre_trained")
    parser.add_argument('--device', default='cpu', type=str, help="choose a device: cpu, cuda, dml")
    args = parser.parse_args()
    # # 重命名之前的模型 TextCNN_Beta
    # os.rename()
    run(args)
