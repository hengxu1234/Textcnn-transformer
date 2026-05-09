# -*- coding: utf-8 -*-
# @AUTHOR  : 玖月
import json

if __name__ == '__main__':
    bianti = {}
    with open('bianti.txt', 'r', encoding='utf-8') as f:
        for line in f.readlines():
            print(line)
            r, b = line.strip().split('\t')
            r = r.lower()
            b = b.lower()
            if bianti.get(b, None):
                print(r, b, bianti[b])
            else:
                bianti[b] = r

    with open('../../app/config/bianti_vocab.json', 'w', encoding='utf-8') as bf:
        bf.write(json.dumps(bianti, ensure_ascii=False))


    # with open('../../app/config/bianti_vocab.json', 'r', encoding='utf-8') as f:
    #     bianti_vocab = json.loads(f.readlines()[0])
    #     with open('bianti.txt', 'w', encoding='utf-8') as bf:
    #         for k, v in bianti_vocab.items():
    #             bf.write('{}\t{}\n'.format(v, k))

