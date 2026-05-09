Precision, Recall and F1-Score...
              precision    recall  f1-score   support

    positive     0.9568    0.9547    0.9557     16000
    negative     0.9548    0.9569    0.9558     16000

    accuracy                         0.9558     32000
   macro avg     0.9558    0.9558    0.9558     32000
weighted avg     0.9558    0.9558    0.9558     32000

Confusion Matrix...
[[15275   725]
 [  690 15310]]
Time usage:  0:00:05


conda create -n ad_detect python=3.7
conda activate ad_detect

数据处理：
cd ad_detect/ml/processed_data/

python process_data.py（old_train.txt最后一行要多一行空行，否则会报错）

python pinyin_utils.py

python strokes_utils.py

训练：
cd ml

python run.py

预测：

python predict.py

安装cpu版本torch:
pip install -r requirements.txt
运行api:
python ad_detect.py

接口：
http://localhost:3002/v1/inference  post请求
使用apifox访问：
参数：
{
    "score_threshold": 0.8,
    "nickname": "yy",
    "text": "加vx：1551112331"
    
}

如果需要训练，安装gpu：
pip install -r requirements.txt
然后卸载cpu版本的三个torch包：
pip uninstall torch torchvision torchaudio
然后安装gpu版本的torch：
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu116
训练之前验证一下gpu是否可用
然后训练：
cd ml
python run.py

self.batch_size = 256在4G显存可以运行
显存够大可以调大batch_size
Epoch可以改成10减少训练时间


项目介绍：
广告防拉人模型
 开发深度学习模型，识别玩家聊天内容中的是否为广告拉人行为，国内使用textcnn模型，主要训练中文数据集，海外使用distilbert-base-multilingual-cased模型训练多语言数据集
1、    整理训练数据，训练时先将所有数据按照8:1:1的比例划分训练集、验证集和测试集
2、    开发模型结构，海外模型使用bert蒸馏模型，在模型的最后一个输出层添加一个二分类的DNN结构用于二分类任务，国内模型使用textcnn训练中文字符的拼音和笔画，在模型中添加一层transformer结构
3、    对模型进行训练，设置合理的batch_size、学习率、dropout值，完成训练后保存模型到本地
4、    加载训练好的模型，对测试集进行预测，使用sklearn库计算准确率、召回率和F1指标，最终模型预测的准确率和召回率在95%以上
主要技术：flask、datasets、transformers、sklearn、pytorch、CrossEntropyLoss、numpy

主要业绩：港台地区使用的是繁体字，难以训练笔画需要使用第三方库转化成简体字

添加transformer结构，将训练集的准确率从96%提升到99%