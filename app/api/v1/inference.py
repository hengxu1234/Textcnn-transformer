# -*- coding: utf-8 -*-
# @AUTHOR  : 玖月
import time

from flask import current_app

from app.libs.error_code import Success
from app.libs.redprint import RedPrint
from app.validators.forms import InferenceForm
from predict import Predict
from zhconv import convert

inference_api = RedPrint('inference')


@inference_api.route('', methods=['POST'])
def inference():
    form = InferenceForm().validate_for_api()
    text = form.text.data
    bianti_vocab = current_app.config["BIANTI_VOCAB"]
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

    batch_data = [text]
    res = Predict.run_batch(current_app.config['SERVER_CONFIG'], batch_data, form.score_threshold.data)
    return Success(data=res)
