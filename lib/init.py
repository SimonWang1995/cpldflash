import os
import argparse
import ipaddress
from lib import gloval
from lib import reboot
from lib import pdu_control as pductl
from lib.configparser import *


curdir = os.path.dirname(__file__)
homedir = os.path.split(curdir)[0]
vercmp_log = os.path.join(homedir, 'reports/version_compare.log')
logcmp_errlog = os.path.join(homedir, 'reports/logscompare_error.log')
summary_log = os.path.join(homedir, 'reports/summary.log')
logpath = os.path.join(homedir, 'reports')


def get_opt():
    parser = argparse.ArgumentParser(description='CPLD firmware Upgrade and downgrade')
    parser.add_argument('-p', '--power_mode', dest='mode', choices=['ac', 'dc'], default='dc',
                        help="Set power cycle mode")
    parser.add_argument('-l', '--loops', dest='loops', type=int, default=1,
                        help='Set flash cycle times(default:%(default)s)')
    parser.add_argument('-d', '--device', dest='device', nargs='+', choices=['MLB', '2BP', '12BP'], default=['MLB'],
                        help='Set flash device(default:%(default)s)')
    groupA = parser.add_argument_group('Ignore error, continue program')
    groupA.add_argument('--ignore', action='store_true', help='Ignore error')
    groupB = parser.add_argument_group('for out band flash')
    groupB.add_argument('-H', dest='ip', type=ipaddress.ip_address, help="BMC ip address")
    groupB.add_argument('-U', dest='username', help="BMC user name")
    groupB.add_argument('-P', dest='password', help='BMC user password')
    args = parser.parse_args().__dict__
    if not args['ip'] and not args['username'] and not args['password']:
        pass
    else:
        if args['ip'] and args['username'] and args['password']:
            cmd = 'ipmitool -H {ip} -U {username} -P {password} raw 6 1 2>&1 >/dev/null'.format(
                ip=args['ip'], username=args['username'], password=args['password'])
            if not os.system(cmd):
                gloval.set_outflag(True)
                gloval.set_ip(args['ip'])
                gloval.set_username(args['username'])
                gloval.set_password(args['password'])
            else:
                print("Error: Excute %s fail, Please check it!" % cmd)
                exit(2)
        else:
            print('ip or username or password is empty')
            exit(2)
    gloval.set_powermode(args['mode'])
    gloval.set_loops(args['loops'])
    gloval.set_devices(args['device'])


def init():
    gloval.set_homedir(homedir)
    gloval.set_logdir(logpath)
    get_opt()


def power_ctl():
    if not gloval.get_outflag():
        if gloval.get_powermode() == 'dc':
            reboot.dccycle()
        if gloval.get_powermode() == 'ac':
            reboot.accycle()
    else:
        if gloval.get_powermode() == 'dc':
            os.system('ipmitool -H {ip} -U {username} -P {password} chassis power cycle'.format(
                ip=gloval.get_ip(), username=gloval.get_username(), password=gloval.get_password()
            ))
        if gloval.get_powermode() == 'ac':
            pductl.PDU_Ctl().accycle(load_config('PDU_Inlet'))


def fopen(file, text='', mode='r'):
    if mode=='w' or mode=='a':
        with open(file, mode) as f:
            f.write(text)
    else:
        with open(file, mode) as f:
            text = f.read()
    return text


def save_log(file, msgs):
    with open(file, 'a') as fp:
        for msg in msgs:
            fp.writelines(msg+'\n')


def clear_reports(path):
    file_list = os.listdir(path)
    if file_list:
        for dir in file_list:
            dir = os.path.join(path, dir)
            if os.path.isdir(dir):
                clear_reports(dir)
            if os.path.isfile(dir):
                os.remove(dir)