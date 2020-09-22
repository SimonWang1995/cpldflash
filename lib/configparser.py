import os
from lib import yaml
from lib import gloval

def load_config(dev):
    fp = open(gloval.get_homedir() + '/config.yaml')
    cfg = yaml.load(fp, Loader=yaml.FullLoader)
    dev_cfg = cfg[dev]
    if dev in ['MLB', '2BP', '12BP', 'PSU']:
        know_dict = cfg['product']
        dev_cfg[0].update({'product': cfg['product']})
        dev_cfg[1].update({'product': cfg['product']})
        return dev_cfg

def load_cache():
    cache_file = os.path.join(gloval.get_homedir(), 'tmp/cache_image.yaml')
    fp = open(cache_file)
    cache = yaml.load(fp, Loader=yaml.FullLoader)
    return cache

def dump_cache(db):
    cache_file = os.path.join(gloval.get_homedir(), 'tmp/cache_image.yaml')
    fp = open(cache_file, 'w')
    cache = yaml.dump(db, fp)
    fp.close()

if __name__ == '__main__':
    curdir = os.path.dirname(__file__)
    homedir = os.path.split(curdir)[0]
    gloval.set_homedir(homedir)
    print(load_config('2BP'))


