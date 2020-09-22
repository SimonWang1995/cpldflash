import os
import time
import subprocess
from lib import gloval

def inreboot():
    ret, out = subprocess.getstatusoutput('ls ' + gloval.get_logdir() + '/rebootcounter')
    if ret != 0:
        return 0
    else:
        return 1

def wrcounter(count):
    with open(os.path.join(gloval.get_logdir(), 'rebootcounter'), 'w') as f:
        f.writelines('%s\n' % str(count))


def rdcounter():
    with open(os.path.join(gloval.get_logdir(), 'rebootcounter'), 'r') as f:
        count = int(f.read())
        return count


def stop():
    """
    Remove Counter
    """
    subprocess.getstatusoutput('rm -rf ' + gloval.get_logdir() + '/rebootcounter')
    ret, runlevel = subprocess.getstatusoutput("runlevel |awk '{print$2}'")
    autobootfile = '/etc/rc.d/init.d/reboottest'
    rcdfile = '/etc/rc' + runlevel + '.d/S99reboottest'
    subprocess.getstatusoutput('rm -rf ' + autobootfile)
    subprocess.getstatusoutput('rm -rf ' + rcdfile)
    

def cycle(action):
    re = open(gloval.get_logdir() + '/rebootcounter', 'r')
    Times = int(re.read())
    re.close()
    if Times >= gloval.get_loops()*2:
        stop()
        return
    else:
        wrcounter(Times+1)
        kkpid = str(os.getpid())
        ret, pythonbin = subprocess.getstatusoutput('ps ' + kkpid + "|grep flashcpld.py|awk '{print$5}'")
        ret, kkpycbool = subprocess.getstatusoutput('ps ' + kkpid + '|grep flashcpld.pyc|wc -l')
        if kkpycbool == '1':
            mainfunc = 'flashcpld.pyc'
        else:
            mainfunc = 'flashcpld.py'
        arg_powermode = '-p ' + gloval.get_powermode()
        arg_loops = '-l ' + str(gloval.get_loops())
        arg_device = '-d ' + ' '.join(gloval.get_devices())
        args = ' '.join([arg_powermode, arg_loops, arg_device])
        if gloval.get_ignore():
            args += ' --ignore'
        cmd = 'nohup ' + pythonbin + ' ' + os.path.join(gloval.get_homedir(), mainfunc) + ' ' + args + ' >> /tmp/flashcpld_log 2>&1 &'
        ret, runlevel = subprocess.getstatusoutput("runlevel |awk '{print$2}'")
        autobootfile = '/etc/rc.d/init.d/reboottest'
        rcdfile = '/etc/rc' + runlevel + '.d/S99reboottest'
        ret, out = subprocess.getstatusoutput('echo "#!/bin/bash" > ' + autobootfile)
        ret, out = subprocess.getstatusoutput('echo "' + cmd + '" >> ' + autobootfile)
        ret, out = subprocess.getstatusoutput('echo "sleep 1s" >> ' + autobootfile)
        ret, out = subprocess.getstatusoutput('chmod 777 ' + autobootfile)
        ret, out = subprocess.getstatusoutput('ln -s ' + autobootfile + ' ' + rcdfile)
        ret, out = subprocess.getstatusoutput('sync')
        time.sleep(2)
        os.system(action)
        time.sleep(10000)
        return


def dccycle():
    cycle('ipmitool chassis power cycle')


def accycle():
    cycle('ac')
