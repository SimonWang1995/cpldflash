import time
import os
from lib import gloval
import subprocess

curdir = os.path.dirname(__file__)
homedir = os.path.split(curdir)[0]
logdir = os.path.join(homedir, 'cyclelogs')
sublogdir = os.path.join(logdir, 'logs')
error_log = os.path.join(logdir, 'error.log')


ipmitool = 'ipmitool'
if gloval.get_outflag():
    ipmitool = "ipmitool -H {ip} -U {username} -P {password} ".format(
        ip=gloval.get_ip(), username=gloval.get_username(), password=gloval.get_password()
    )
bmc_cmd = {'sel': '{ipmitool} sel list'.format(ipmitool=ipmitool),
           'sdr': '{ipmitool} sdr list'.format(ipmitool=ipmitool),
           'fru': '{ipmitool} fru list'.format(ipmitool=ipmitool)}

name_array = ['pci', 'disks', 'cpu_procs', 'cpu_cores', 'cpu_speed', 'total_memory', 'memory', 'ipmi_lan',
              'ipmi_sol', 'ipmi_bmc', 'dmidecode_type_0', 'dmidecode_type_1', 'dmidecode_type_2',
              'dmidecode_type_3', 'ipmi_restart_cause', 'ipmi_power_restore_police', 'lspcivvv']
# these are the tests
lspci_nn_vvv = 'lspci -nn -vvv | grep -e "[[:alnum:]][[:alnum:]]:[[:alnum:]][[:alnum:]].[[:alnum:]] " ' \
               '-e "LnkSta" -e "LnkCtl" -e "UESta" -e "CESta"'
test_array = ['lspci', 'ls /dev/disk/by-id', 'grep -ci processor /proc/cpuinfo',
              'grep -ci cores /proc/cpuinfo', 'dmidecode -t processor', 'grep MemTotal /proc/meminfo',
              'dmidecode -t memory', 'ipmitool lan print', 'ipmitool sol info 1', 'ipmitool mc info',
              'dmidecode -t 0', 'dmidecode -t 1', 'dmidecode -t 2', 'dmidecode -t 3',
              'ipmitool raw 0x00 0x07', 'ipmitool raw 0x00 0x01', lspci_nn_vvv]
commandsdict = dict(zip(name_array, test_array))

def init():
    local_res = 'PASS'
    local_com = ['']
    for name, cmd in bmc_cmd.items():
        _logdir = os.path.join(logdir, name+'_log')
        os.system('rm -fr ' + _logdir + " 2>&1 > /dev/null")
        os.makedirs(_logdir)
        ret, out = subprocess.getstatusoutput(cmd)
        if ret != 0:
            local_res = 'FAIL'
            local_com.append(name + ' command: ' + cmd)
        logsave(os.path.join(_logdir, name+'.log.1'), out)
        logsave(os.path.join(logdir, name + '_full.log'), out)
    os.system('rm -fr ' + sublogdir + " 2>&1 > /dev/null")
    if not gloval.get_outflag():
        os.makedirs(sublogdir)
        for name, cmd in commandsdict.items():
            ret, out = subprocess.getstatusoutput(cmd)
            if ret != 0:
                local_res = 'FAIL'
                local_com.append(name + ' command: ' + cmd)
            logsave(os.path.join(sublogdir, name + '.log.1'), out)
    return (local_res, local_com)


def logsave(file, log):
    with open(file, 'w') as f:
        f.write(log)


def logread(file):
    with open(file, 'r') as f:
        log = f.read()
    return log


def compare(count):
    local_res = 'PASS'
    local_comment = []
    for name, cmd in bmc_cmd.items():
        _logdir = os.path.join(logdir, name + '_log')
        ret, out = subprocess.getstatusoutput(cmd)
        logsave(os.path.join(_logdir, name + '.log.'+str(count)), out)
        logsave(os.path.join(logdir, name+'_full.log'), out)
        if name == 'sel':
            org = getSelList(logread(os.path.join(_logdir, 'sel.log.1')))
            last = getSelList(logread(os.path.join(_logdir, 'sel.log.'+str(count))))
        elif name == 'sdr':
            org = getSdrDict(logread(os.path.join(_logdir, 'sdr.log.1')))
            last = getSdrDict(logread(os.path.join(_logdir, 'sdr.log.' + str(count))))
        else:
            org = logread(os.path.join(_logdir, name+'.log.1'))
            last = logread(os.path.join(_logdir, name+'.log.' + str(count)))
        if not comparelog(org, last):
            msg = """An error was detected in test {name} on reboot #{count} logged {date}
                                   See {name}.log.{count} for more details.""".format(name=name, count=str(count),
                                                                                      date=time.strftime(
                                                                                          '%Y%m%dT%H%M%S'))
            local_res = 'FAIL'
            local_comment.append(msg)
    if not gloval.get_outflag():
        for name, cmd in commandsdict.items():
            ret, out = subprocess.getstatusoutput(cmd)
            org = logread(os.path.join(sublogdir, name + '.log.1'))
            last = out
            if not comparelog(org, last):
                logsave(os.path.join(sublogdir, name + '.log.'+str(count)), out)
                msg = """An error was detected in test {name} on reboot #{count} logged {date}
                                   See {name}.log.{count} for more details.""".format(name=name, count=str(count),
                                                                                      date=time.strftime(
                                                                                          '%Y%m%dT%H%M%S'))
                local_res = 'FAIL'
                local_comment.append(msg)

    return (local_res, local_comment)


def comparelog(string1, string2):
    if string1 == string2:
        return True
    else:
        return False

def getSdrDict(input):
    '''
    This returns the 1st and 3rd columns of the sdr output as dict.
    '''
    sdrDict = {}
    # Truncate last new line
    input = input[0:len(input) - 1]
    for line in input.split('\n'):
        sdrDict[line.split('|')[0]] = line.split('|')[2]
    return sdrDict

def getSelList(input):
    '''
    This returns the 1st and 3rd columns of the sel output as list.
    '''
    sellist = []
    # Truncate last new line
    input = input[0:len(input) - 1]
    for line in input.split('\n'):
        sellist.append("|".join(line.split('|')[3:]))
    return sellist
