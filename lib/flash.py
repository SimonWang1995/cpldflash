import os
import re
import logging
import subprocess
from textwrap import dedent
from lib import gloval
from lib.configparser import load_config


curdir = os.path.dirname(__file__)
homedir = os.path.split(curdir)[0]


class Flash(object):
    def __init__(self, dev):
        self.dev = dev
        self.cfg = load_config(dev)
        self.flash_log = os.path.join(homedir, 'reports/flash.log')
        self.initlog()
        self.toolpath = os.path.join(homedir, 'tools')
        self.tool = 'FlashTool64Bit'
        self.getver_cmd = '{tool} -p {product} -t cpld -i {index} -v'.format(tool=self.tool,
                                                                             product=self.cfg[0]['product'],
                                                                             index=self.cfg[0]['index'])
        if gloval.get_outflag():
            self.getver_rawcmd = "{tool} -H {ip} -U {username} -P {password} -p {product} -t cpld -i {index} -v"
            self.getver_cmd = self.getver_rawcmd.format(tool=self.tool, ip=gloval.get_ip(), username=gloval.get_username(),
                                  password=gloval.get_password(), product=self.cfg[0]['product'], index=self.cfg[0]['index'])

    def pre_flash(self):
        self.make_flashcmd(0)
        os.chdir(self.toolpath)
        print('')
        print('Starting Pre-Flash as following Info:')
        print('  Flash Tool Path: ' + self.toolpath)
        print('  Current Location: ' + os.getcwd())
        print('  Execute Command:')
        print('   ' + self.flash_cmd)
        print('')
        if os.path.exists(self.tool):
            os.chmod(self.tool, 777)
        else:
            print('No such tool: ' + os.path.join(self.toolpath, self.tool))
            exit(2)
        if not os.path.exists(self.cfg[0]['image']):
            print('No such image: ' + self.cfg[0]['image'])
            exit(2)
        if os.system('./' + self.flash_cmd):
            print('pre flash fail, please check it')
            exit(2)

    def make_flashcmd(self, index):
            self.flash_rawcmd = "{tool} -p {product} -t cpld -i {index} -f {image}"
            self.getver_rawcmd = '{tool} -p {product} -t cpld -i {index} -v'
            if gloval.get_outflag():
                self.flash_rawcmd = "{tool} -H {ip} -U {username} -P {password} -p {product} -t cpld -i {index} -f {image}"
                self.getver_rawcmd = "{tool} -H {ip} -U {username} -P {password} -p {product} -t cpld -i {index} -v"
            self.flash_cmd = self.flash_rawcmd.format(tool=self.tool, ip=gloval.get_ip(), username=gloval.get_username(),
                                  password=gloval.get_password(), product=self.cfg[index]['product'], index=self.cfg[index]['index'],
                                                      image=self.cfg[index]['image'])
            self.getver_cmd = self.getver_rawcmd.format(tool=self.tool, ip=gloval.get_ip(), username=gloval.get_username(),
                                  password=gloval.get_password(), product=self.cfg[index]['product'], index=self.cfg[index]['index'])

    def get_version(self):
        os.chdir(self.toolpath)
        ret, out = subprocess.getstatusoutput('./'+self.getver_cmd)
        if ret != 0:
            print('FAIL at run get version cmd:' + self.getver_cmd)
            exit(2)
        comp = re.compile('CPLD VERSION:(.*)')
        return comp.search(out).groups()[0].split()[-1]

    def select_image(self):
        self.curver = self.get_version()
        if self.curver == self.cfg[0]['version']:
            self.make_flashcmd(1)
            self.flash_version = self.cfg[1]['version']
            self.flash_image = self.cfg[1]['image']
            self.op = 'Upgrade'
        else:
            self.make_flashcmd(0)
            self.flash_version = self.cfg[0]['version']
            self.flash_image = self.cfg[0]['image']
            self.op = 'Download'

    def initlog(self):
        logging.basicConfig(filename=self.flash_log, level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger()

    def display(self):
        text = dedent("""
                 ====================== Flash Info ==================
                 Flash Device: {0}
                 Flash Operation: {1}
                 Current Firmware: {2}
                 Upgrate Firmware: {3}
                 Upgrade Image: {4}
                 """.format(self.dev, self.op, self.curver, self.flash_version, self.flash_image))
        self.logger.info(text)

    def flash(self):
        self.select_image()
        self.display()
        os.chdir(self.toolpath)
        print('')
        self.logger.info('Starting Flash as following Info:')
        self.logger.info('  Flash Tool Path: ' + self.toolpath)
        self.logger.info('  Current Location: ' + os.getcwd())
        self.logger.info('  Execute Command:')
        self.logger.info('   ' + self.flash_cmd)
        print('')
        if not os.path.exists(self.tool):
            self.logger.error(" %s No found" % self.tool)
            exit(2)
        if not os.path.exists(self.flash_image):
            self.logger.error("Image %s No found" % self.flash_image)
            exit(2)
        self.fopen(self.flash_log, '{0} firmware {1} \n'.format(self.dev, self.op), mode='a')
        last_flashlog = os.path.join(homedir, 'tmp/flash.log')
        cmd = './' + self.flash_cmd + " 2>&1 | tee " + last_flashlog
        os.system(cmd)
        os.system("cat %s >> %s" % (last_flashlog, self.flash_log))
        if re.search('(fail|error)', self.fopen(last_flashlog), re.I):
            errmsg = "Flash {0} firmware {1} ********** [ FAIL ]".format(self.dev, self.op)
            self.logger.error(errmsg)
            os.remove(last_flashlog)
            os.chdir(homedir)
            return False
        else:
            passmsg = "Flash {0} firmware {1} ************ [ PASS ]".format(self.dev, self.op)
            # self.fopen(self.fault_log, passmsg, mode='a')
            self.logger.info(passmsg)
            os.remove(last_flashlog)
            os.chdir(homedir)
            return True


    @staticmethod
    def fopen(file, content='', mode='r'):
        if mode == 'w' or mode == 'a':
            with open(file, mode) as fp:
                fp.write(content)
        elif mode == 'r':
            with open(file, mode) as fp:
                content = fp.read()
                print(content)
            return content


if __name__ == '__main__':
    pass


