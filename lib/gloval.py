
class GloVal(object):
    loops = int()
    homedir = 'default'
    logpath = 'default'
    powermode = 'default'
    devices = list()
    outband = False
    ignore = False
    ip = 'default'
    username = 'default'
    password = 'default'


def get_homedir():
    return GloVal.homedir


def set_homedir(db):
    GloVal.homedir = db


def get_logdir():
    return GloVal.logpath


def set_logdir(db):
    GloVal.logpath = db


def get_loops():
    return GloVal.loops


def set_loops(db):
    GloVal.loops = db


def get_powermode():
    return GloVal.powermode


def set_powermode(db):
    GloVal.powermode = db


def get_devices():
    return GloVal.devices


def set_devices(db):
    GloVal.devices = db


def get_ip():
    return GloVal.ip


def set_ip(db):
    GloVal.ip = db


def get_username():
    return GloVal.username


def set_username(db):
    GloVal.username = db


def get_password():
    return GloVal.password


def set_password(db):
    GloVal.password = db


def get_outflag():
    return GloVal.outband


def set_outflag(db):
    GloVal.outband = db


def get_ignore():
    return GloVal.ignore


def set_ignore(db):
    GloVal.ignore = db