import os
import json
import hmac
import hashlib


def change_owner(path, uid=None, gid=None):
    if uid is None:
        uid = -1

    if gid is None:
        gid = -1

    if (uid, gid) == (-1, -1):
        return

    stats = os.stat(path)
    if (uid in (-1, stats.st_uid)) and (gid in (-1, stats.st_gid)):
        return

    logging.debug('will chown %s -> (%s , %d)', path, uid, gid)
    os.chown(path, uid, gid)


def change_permissions(p, chmod=None, uid=None, gid=None):
    if chmod:
        os.chmod(p, chmod)

    change_owner(p, uid, gid)


def writefile(p, data, chmod=None, uid=None, gid=None):
    tmp = p + '_tmp'

    try:
        os.makedirs(os.path.dirname(p))
    except OSError:
        pass

    with open(tmp, 'wb') as f:
        f.write(data)
        change_permissions(tmp, chmod, uid, gid)

    os.rename(tmp, p)


def readfile(path):
    return open(path, 'rb').read()


def md5data(d):
    return hashlib.md5(d).hexdigest()


def dump_dict(data):
    return json.dumps(data, sort_keys=True).encode('utf-8')


def dict_hash(data):
    return md5data(dump_dict(data))


def sign(key, data):
    return hmac.new(key=key.encode('utf-8'), msg=dump_dict(data)).hexdigest()


def safe_password(username, password):
    return dict_hash({'username': username, 'password': password})
