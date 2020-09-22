import time
from lib.flash import Flash
from lib import testlog as logger
from lib import logcompare as cyclelog
from lib.init import *


def main():
    init()
    if not gloval.get_outflag():
        if reboot.inreboot() == 0:
            for dev in gloval.get_devices():
                Flash(dev).pre_flash()
                reboot.wrcounter(0)
        else:
            count = reboot.rdcounter()
            if count != 1:
                ver_compare(count)
            cycle = str((count + 1)//2) + '-' + str((count+1) % 2)
            flash_devs(cycle)
            cyclelog_compare(count)
        os.system('ipmitool sel clear')
        power_ctl()
    else:
        count = 1
        while count <= gloval.get_loops()*2:
            os.system('ipmitool -H {ip} -U {username} -P {password} sel clear'.format(ip=gloval.get_ip(),
                                                                                      username=gloval.get_username(),
                                                                                      password=gloval.get_password()))
            cycle = str((count + 1)//2) + '-' + str((count+1) % 2)
            flash_devs(cycle)
            power_ctl()
            wait_sys_up()
            ver_compare(count)
            cyclelog_compare(count)
            count += 1


def flash_devs(cycle):
    cache_img = dict()
    logger.title("Start #{cycle} flash ".format(cycle=cycle) + ' '.join(gloval.get_devices()))
    fopen(vercmp_log, 'Cycle #' + cycle + '\n', 'a')
    fopen(summary_log, 'Cycle #' + cycle + '\n', 'a')
    for dev in gloval.get_devices():
        flasher = Flash(dev)
        fopen(flasher.flash_log, 'Cycle #' + cycle + '\n', 'a')
        flasher.flash()
        cache_img[dev] = flasher.flash_version
    dump_cache(cache_img)


def cyclelog_compare(count):
    if count == 1:
        logger.info('start init compare log')
        ret, out = cyclelog.init()
        if ret != 'PASS':
            for com in out:
                logger.error(com)
            exit(2)
    else:
        ret, comment = cyclelog.compare(count)
        if ret != 'PASS':
            fopen(summary_log, 'logs compare ------ [ FAIL ]\n', 'a')
            save_log(logcmp_errlog, comment)
            for i in comment:
                logger.error(i)
        else:
            fopen(summary_log, 'logs compare ------ [ PASS]\n', 'a')


def ver_compare(count):
    ret, out = compare_ver()
    if ret == 'FAIL':
        fopen(summary_log, 'version compare ------ [ FAIL ]\n', 'a')
    else:
        fopen(summary_log, 'version compare ------ [ PASS]\n', 'a')


def compare_ver():
    res = 'PASS'
    com = []
    cache_ver = load_cache()
    for dev in gloval.get_devices():
        flasher = Flash(dev)
        curver = flasher.get_version()
        if cache_ver[dev] != curver:
            res = 'FAIL'
            ret = dev + ' version compare FAIL.'
            com.append(ret)
            logger.error(ret)
            logger.error(' - Current: ' + curver)
            logger.error(' - Criteria: ' + cache_ver[dev])
            msgs = [
                ret,
                ' - Current: ' + curver,
                ' - Criteria: ' + cache_ver[dev],
                ' - Datetime: {0}'.format(time.strftime('%Y-%m-%dT%H:%M:%S')),
                '='*80
            ]
            save_log(vercmp_log, msgs)
        else:
            ret = dev + 'version compare PASS.'
            logger.info(ret)
            logger.info(' - Current: ' + curver)
            logger.info(' - Criteria: ' + cache_ver[dev])
            msgs = [
                ret,
                ' - Current: ' + curver,
                ' - Criteria: ' + cache_ver[dev],
                ' - Datetime: {0}'.format(time.strftime('%Y-%m-%dT%H:%M:%S')),
                '='*80
            ]
            save_log(vercmp_log, msgs)
    return (res, com)


def wait_sys_up():
    """Wait system power up, via sel  detect power up"""
    ipmitool = 'ipmitool -H {ip} -U {username} -P {password}'.format(ip=gloval.get_ip(),
                                                                     username=gloval.get_username(),
                                                                     password=gloval.get_password())
    logger.info("Wait system power up")
    time.sleep(60)
    for i in range(0, 16):
        if int(os.popen("{ipmitool} sel list | grep -c 'power up'".format(ipmitool=ipmitool)).read().strip()) == 1:
            break
        time.sleep(20)
        if i == 15:
            logger.error("System can not power up")
            exit(2)


if __name__ == '__main__':
    main()
