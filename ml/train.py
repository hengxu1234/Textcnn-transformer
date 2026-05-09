# -*- coding: utf-8 -*-
"""
@Author  : 玖月
@File    : train.py
@Date    : 2021/8/4 10:22
@Desc    : 
"""
import time

import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import torch
from sklearn import metrics
from tensorboardX import SummaryWriter
from tqdm import tqdm

# script.py
import sys
import os

# 获取项目根目录（找到app所在的目录）
# 以下代码会自动定位到app的父目录（项目根目录）
current_file_path = os.path.abspath(__file__)  # 得到当前脚本的绝对路径
subdir_path = os.path.dirname(current_file_path)  # 得到subdir的路径
project_root = os.path.dirname(subdir_path)  # 得到project根目录（app的父目录）

# 将项目根目录添加到Python的搜索路径
sys.path.append(project_root)

from ml.utils.time_utils import get_time_dif


def init_network(model, method='xavier', exclude='embedding'):
    """
    权重初始化  默认初始化方法: xavier
    Parameters
    ----------
    model :
    method :
    exclude :

    Returns
    -------

    """
    for name, w in model.named_parameters():
        if exclude not in name:
            if 'weight' in name:
                if method == 'xavier':
                    nn.init.xavier_normal_(w)
                elif method == 'kaiming':
                    nn.init.kaiming_normal_(w)
                else:
                    nn.init.normal_(w)
            elif 'bias' in name:
                nn.init.constant_(w, 0)
            else:
                pass


def evaluate(config, model, dataloader, test=False):
    """
    验证函数
    Parameters
    ----------
    config : 超参数
    model : model
    dev_dataloader : 验证集
    test : 是否是测试集

    Returns
    -------

    """
    model.eval() #设置为评估模式
    total_loss = 0
    predict_all = np.array([], dtype=int)
    labels_all = np.array([], dtype=int)

    with torch.no_grad():
        for step, batch in enumerate(dataloader):
            text, label = batch

            outputs = model(text)#相当于model.forward(text)

            # loss
            cross_entropy_loss = nn.CrossEntropyLoss()#一个实例
            loss = cross_entropy_loss(outputs, label)

            total_loss += loss
            label = label.data.cpu().numpy()
            predict = torch.max(outputs.data, 1)[1].cpu().numpy()#取一维最大值的索引

            labels_all = np.append(labels_all, label)
            predict_all = np.append(predict_all, predict)

    accuracy = metrics.accuracy_score(labels_all, predict_all)

    if test:
        report = metrics.classification_report(labels_all, predict_all, target_names=config.class_list, digits=4)

        # 困惑矩阵
        confusion = metrics.confusion_matrix(labels_all, predict_all)

        return accuracy, total_loss / len(dataloader), report, confusion
    return accuracy, total_loss / len(dataloader)


def test(config, model, dataloader):
    # 加载模型
    model.load_state_dict(torch.load(config.save_model_path))
    model.eval()
    start_time = time.time()
    test_acc, test_loss, test_report, test_confusion = evaluate(config, model, dataloader, test=True)
    
    msg = 'Test Loss: {0:>5.2}, Test Accuracy: {1:>6.2}'
    print("Precision, Recall and F1-Score...")
    print(test_report)
    print("Confusion Matrix...")
    print(test_confusion)
    time_dif = get_time_dif(start_time)
    print("Time usage: ", time_dif)
    test_res = {
        "test_loss": test_loss,
        "test_acc": test_acc
    }
    return test_res


def train(config, model, train_dataloader, dev_dataloader, test_dataloader):
    start_time = time.time()
    model.train()
    # 优化器
    optimizer = torch.optim.Adam(model.parameters(), lr=config.learning_rate)
    # 记录当前 batch
    total_batch = 0
    # 记录 dev best loss
    dev_best_loss = float('inf')

    # 记录最新 dev loss 有下降的 batch 数值, 即属于第几个 batch
    last_improve = 0

    # 记录是否很久没有提升效果了  即 loss 很久没有下降
    truncate_flag = False

    # 暂时禁用 tensorboardX 可视化
    # writer = SummaryWriter(log_dir=config.log_path + '/' + time.strftime("%m-%d_%H-%M", time.localtime()))

    # 训练
    for epoch in range(config.num_epochs):
        print('Epoch [{}/{}]'.format(epoch+1, config.num_epochs))

        for i, batch in tqdm(enumerate(train_dataloader), desc=f'Epoch : {epoch}', total=len(train_dataloader)):
            text, label = batch

            outputs = model(text)
            model.zero_grad()

            loss = F.cross_entropy(outputs, label)
            # 添加调试信息
            print(f"Loss shape: {loss.shape}, Loss type: {type(loss)}")
            loss.backward()
            optimizer.step()

            if total_batch % 5 == 0:
                #每隔 100 步验证一次
                y_true = label.data.cpu()
                y_pred = torch.max(outputs.data, 1)[1].cpu()
                train_accuracy = metrics.accuracy_score(y_true, y_pred)

                # 验证集
                dev_accuracy, dev_loss = evaluate(config, model, dev_dataloader)

                if dev_loss < dev_best_loss:
                    dev_best_loss = dev_loss
                    # 保存模型
                    torch.save(model.state_dict(), config.save_model_path)
                    improve = '*'
                    last_improve = total_batch  # 记录更新步数
                else:
                    improve = ''
                time_dif = get_time_dif(start_time)

                # 打印输出
                msg = 'Iter: {0:>6}, Train loss: {1:>5.2}, Train Acc: {2:>6.2%}, ' \
                      'Val Loss: {3:>5.2}, Val Acc: {4:>6.2%}, Time: {5} {6}'
                print(msg.format(total_batch, loss.item(), train_accuracy,
                                 dev_loss, dev_accuracy, time_dif, improve))

                # 暂时禁用 tensorboardX 可视化
                # writer.add_scalar("loss/train", loss.detach().item(), total_batch)
                # writer.add_scalar("loss/dev", dev_loss.detach().item(), total_batch)
                # writer.add_scalar("acc/train", train_accuracy, total_batch)
                # writer.add_scalar("acc/dev", dev_accuracy, total_batch)
                model.train()

            total_batch += 1
            if total_batch - last_improve > config.require_improvement:
                # 验证集loss超过1000batch没下降，结束训练, 早停
                print("No optimization for a long time, auto-stopping...")
                truncate_flag = True
                break

        if truncate_flag:
            break
    # 暂时禁用 tensorboardX 可视化
    # writer.close()
    # 测试集测试模型表现
    test_res = test(config, model, test_dataloader)
    return test_res
