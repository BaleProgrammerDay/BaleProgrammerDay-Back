from werkzeug.exceptions import BadRequest, Forbidden
from models import Group, db, Question, Submit, Purchase

import base64
import hashlib
from Crypto import Random
from Crypto.Cipher import AES

class AESCipher(object):

    def __init__(self, key):
        self.bs = AES.block_size
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = b'\x10' * 16
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw.encode()))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return AESCipher._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]

def get_key_from_json_request(j, key):
    if key in j:
        return j[key]
    raise BadRequest(description="field "+key+" is missing")


def authentication_required(request) -> Group:
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith("GroupID "):
        raise Forbidden("Authorization header is missing or malformed")

    group_id = auth_header[len("GroupID "):].strip()

    gr = Group.query.filter_by(id=group_id).first()
    if gr is None:
        raise Forbidden("Group not found")

    return gr

def get_object_or_404(model, **kwargs):
    res = model.query.filter_by(**kwargs).first()
    if res == None:
        raise BadRequest(description="object not found")
    return res

def is_purchased(q_id, g_id):
    return Purchase.query.filter_by(group_id=g_id, question_id=q_id).first() != None

def is_answerd(q_id, g_id):
    return Submit.query.filter_by(group_id=g_id, question_id=q_id, result=True).first() != None

def num_correct_answers(q_id):
    return len(Submit.query.filter_by(question_id=q_id, result=True).all())

KEY = 'K4Tz'
def encrypt_id(q_id, g_id):
    return AESCipher(str(g_id) + KEY).encrypt(str(q_id)).decode('ascii')

def decrypt_id(enc, g_id):
    try:
        q_id = int(AESCipher(str(g_id) + KEY).decrypt(enc.encode('ascii')))
    except:
        raise BadRequest(description="object not found")
    return q_id