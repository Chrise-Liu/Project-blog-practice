"""
    json-web-token的形成方法練習
    1.header
    2.payload
    3.signature
"""
import base64
import json
import time
import copy
import hmac


class Jwt():
    def __init__(self):
        pass

    @staticmethod
    def b64encode(content):
        return base64.urlsafe_b64encode(content).replace(b'=',b'')

    @staticmethod
    def b64decode(b):
        # 如何把去掉的等號加回來
        sem = len(b) % 4
        if sem > 0:
            b += b'=' * (4-sem)
        return base64.urlsafe_b64decode(b)

    @staticmethod
    def encode(payload, key, exp=300):
        # init header
        header = {'typ':'JWT','alg':'HS256'}
        header_json = json.dumps(header,separators=(',',':'), sort_keys=True)
        header_bs = Jwt.b64encode(header_json.encode())

        # init payload
        # 傳進來的字典或許還要用，避免更動別人的字典所以深拷貝一份進行處理
        payload_self = copy.deepcopy(payload)
        # 判斷是否為int或str
        if not isinstance(exp, int) and not isinstance(exp, str):
            raise TypeError('Exp is not int or str !')
        payload_self['exp'] = time.time() + int(exp)
        payload_js = json.dumps(payload_self, separators=(',',':'), sort_keys=True)
        payload_bs = Jwt.b64encode(payload_js.encode())

        # init sign
        if isinstance(key, str):
            key = key.encode()
        hm = hmac.new(key, header_bs + b'.' + payload_bs, digestmod='SHA256')
        sign_bs = Jwt.b64encode(hm.digest())

        return header_bs + b'.' + payload_bs + b'.' + sign_bs

    @staticmethod
    def decode(token, key):
        # 1.校驗簽名  2.檢查exp是否過期  3.return payload部份的解碼
        header_bs, payload_bs, sign_bs = token.split(b'.')
        if isinstance(key, str):
            key = key.encode()
        hm = hmac.new(key, header_bs + b'.' + payload_bs, digestmod='SHA256')
        if sign_bs != Jwt.b64encode(hm.digest()):
            raise KeyError('Invalid Signature')

        # 檢查是否過期
        payload_js = Jwt.b64decode(payload_bs)
        payload = json.loads(payload_js)

        if 'exp' in payload:
            now = time.time()
            if now > payload['exp']:
                raise
        return payload





if __name__ == '__main__':
    token = Jwt.encode({'username':'chrise'}, '123456', 300)
    print(token)


    print('生成token:')
    print(token)
    print('校驗結果:')
    print(Jwt.decode(token, '123456'))