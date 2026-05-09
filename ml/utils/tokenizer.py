# import ahocorasick
import time

import unicodedata
import six
# from janome.tokenizer import Tokenizer


# ja_tokenizer = Tokenizer()


class AllTokenizer(object):
    def __init__(self, do_lower_case=True):
        """Constructs a BasicAllTokenizer.
        Args:
          do_lower_case: Whether to lower case the input.
        """
        self.do_lower_case = do_lower_case

    def tokenize(self, text, drop_prun=True):
        """Tokenizes a piece of text."""
        text = convert_to_unicode(text)
        # print(text)
        text = self._clean_text(text)
        # print(text)
        text = self._tokenize_chinese_chars(str(text))

        orig_tokens = whitespace_tokenize(text)
        split_tokens = []
        for token in orig_tokens:
            if self.do_lower_case:
                token = token.lower()
                token = self._run_strip_accents(token)
            split_tokens.extend(self._run_split_on_punc(token, drop_prun))

        output_tokens = whitespace_tokenize(" ".join(split_tokens))
        # output_text = "\001" + "\001".join(output_tokens) + "\001" if output_tokens else ""
        return output_tokens

    def _run_strip_accents(self, text):
        """Strips accents from a piece of text."""
        text = unicodedata.normalize("NFD", text)
        output = []
        for char in text:
            cat = unicodedata.category(char)
            if cat == "Mn" or cat.startswith("M") or cat.startswith("P") or cat.startswith("S") or cat in {"Cc", "Cf"}:
                continue
            output.append(char)
        return "".join(output)

    def _run_split_on_punc(self, text, drop_prun):
        """Splits punctuation on a piece of text."""
        chars = list(text)
        # print(chars)
        i = 0
        start_new_word = True
        output = []
        while i < len(chars):
            char = chars[i]
            if _is_punctuation(char):
                if not drop_prun:
                    output.append([char])
                start_new_word = True
            else:
                if start_new_word:
                    output.append([])
                start_new_word = False
                output[-1].append(char)
            i += 1

        return ["".join(x) for x in output]

    def _tokenize_chinese_chars(self, text):
        """Adds whitespace around any CJK character."""
        output = []
        # print(text)
        for char in text:
            cp = ord(str(char))
            # print(cp)
            if self._is_chinese_char(cp):
                # print("chinese char: ", char)
                output.append(" ")
                output.append(char)
                output.append(" ")
            else:
                output.append(char)
        # print(output)
        return "".join(output)

    # def _tokenize_ja_chars(self, text):
    #     output = [token.surface for token in ja_tokenizer.tokenize(text)]
    #     # print(output)
    #     return " ".join(output)

    def _is_chinese_char(self, cp):
        """Checks whether CP is the codepoint of a CJK character."""
        # if ((cp >= 0x4E00 and cp <= 0x9FFF) or  #
        #         (cp >= 0x3400 and cp <= 0x4DBF) or  #
        #         (cp >= 0x20000 and cp <= 0x2A6DF) or  #
        #         (cp >= 0x2A700 and cp <= 0x2B73F) or  #
        #         (cp >= 0x2B740 and cp <= 0x2B81F) or  #
        #         (cp >= 0x2B820 and cp <= 0x2CEAF) or
        #         (cp >= 0xF900 and cp <= 0xFAFF) or  #
        #         (cp >= 0x2F800 and cp <= 0x2FA1F)):  #
        #     return True
        if ((cp >= 0x4E00 and cp <= 0xA000) or  # 中日韩统一表意文字
            (cp >= 0x3400 and cp <= 0x4DBF) or  # 中日韩统一表意文字扩充A
            (cp >= 0x3040 and cp <= 0x309F) or  # 日文平假名
            (cp >= 0x30A0 and cp <= 0x30FF) or  # 日文片假名
            (cp >= 0x31F0 and cp <= 0x31FF) or  # 片假名音标扩充
            (cp >= 0xAC00 and cp <= 0xD7AF) or  # 朝鲜文音节
            (cp >= 0x1100 and cp <= 0x11FF) or  # 朝鲜文
            (cp >= 0x3130 and cp <= 0x318F) or  # 朝鲜文兼容字母
            (cp >= 0x0E00 and cp <= 0x0E7F)):  # 泰语
            return True

        return False

    def _clean_text(self, text):
        """Performs invalid character removal and whitespace cleanup on text."""
        output = []
        for char in text:
            cp = ord(str(char))
            if cp == 0 or cp == 0xfffd or _is_control(char):
                continue
            if _is_whitespace(char):
                output.append(" ")
            else:
                output.append(char)
        return "".join(output)


def convert_to_unicode(text):
    """Converts `text` to Unicode (if it's not already), assuming utf-8 input."""
    if six.PY3:
        if isinstance(text, str):
            return text
        elif isinstance(text, bytes):
            return text.decode("utf-8", "ignore")
        else:
            raise ValueError("Unsupported string type: %s" % (type(text)))
    elif six.PY2:
        if isinstance(text, str):
            return text.decode("utf-8", "ignore")
        elif isinstance(text, unicode):
            return text
        else:
            raise ValueError("Unsupported string type: %s" % (type(text)))
    else:
        raise ValueError("Not running on Python2 or Python 3?")


def _is_whitespace(char):
    """Checks whether `chars` is a whitespace character."""
    # \t, \n, and \r are technically contorl characters but we treat them
    # as whitespace since they are generally considered as such.
    if char == " " or char == "\t" or char == "\n" or char == "\r":
        return True
    cat = unicodedata.category(char)
    if cat == "Zs":
        return True
    return False


def _is_control(char):
    """Checks whether `chars` is a control character."""
    # These are technically control characters but we count them as whitespace
    # characters.
    if char == "\t" or char == "\n" or char == "\r":
        return False
    cat = unicodedata.category(char)
    if cat.startswith("C"):
        return True
    return False


def _is_punctuation(char):
    """Checks whether `chars` is a punctuation character."""
    cp = ord(char)
    # We treat all non-letter/number ASCII as punctuation.
    # Characters such as "^", "$", and "`" are not in the Unicode
    # Punctuation class but we treat them as punctuation anyways, for
    # consistency.
    if ((cp >= 33 and cp <= 47) or (cp >= 58 and cp <= 64) or
            (cp >= 91 and cp <= 96) or (cp >= 123 and cp <= 126)):
        return True
    cat = unicodedata.category(char)
    if cat.startswith("P"):
        return True
    return False


def whitespace_tokenize(text):
    """Runs basic whitespace cleaning and splitting on a peice of text."""
    text = text.strip()
    if not text:
        return []
    tokens = text.split()
    return tokens


if __name__ == "__main__":
    t1 = time.time()
    tokenizer = AllTokenizer()
    # text = ['hello', 'today is a nice day', '你好', '我是你爸爸', 'यह एक नमूना संदेश है।', '이 샘플 메시지입니다.',
    #         'Huu', 'ni ujumbe', 'sampuli.', '????', 'vx', 'ckn你'   '好', '看av', 'av']
    #
    text = 'هＬｉｎｅه ：nazp     ه溦ه信ه ；FE08811'
    text = '上面十位数是起俄，我有仝部衤Ｌ孢杩发给你们，来了说下是少三的就行了'
    text = '加盟主🅻́！́🅽́🅴́：@607y（雨漫）或w e chat：yfdt16或ggb640差你啦，誤踢'
    res = tokenizer.tokenize(text)
    res = ''.join(res)
    t2 = time.time()
    print(res, (t2-t1)*1000)
    # ac = build_actree(text)
    # print("\001" + "\001".join("av have a nice day".split(' ')) + "\001")
    # filter_r = ac.iter("\001" + "\001".join(tokenizer.tokenize("vx av have a nice day 看av到这里")) + "\001")
    # for i in filter_r:
    #     print(i)
    #     print(str(i[1]))
    # for i in "ข้อความนี้เป็นข้อความตัวอย่าง":
    #     print(i)

    # from transformers import XLMTokenizer
    # tokenizer = XLMTokenizer.from_pretrained("xlm-mlm-100-1280")
    # print(tokenizer.tokenize("こんにちは、はじめまして 여보세요 만나서 반가워요 hello i have a pen 你是煞笔吗？"))
