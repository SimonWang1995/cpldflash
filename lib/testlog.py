import os
import time
import logging
scriptVersion = 'V01'
author = ''
tel = '+86'

Date = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
curdir = os.path.dirname(__file__)
homedir = os.path.split(curdir)[0]
log = '{0}/reports/{1}-log'.format(homedir, 'CPLD_Flash')
FORMAT = '%(asctime)s |%(levelname)6s | - %(message)s'
DATEFMT = '%Y-%m-%d %H:%M:%S'
logging.basicConfig(level=logging.DEBUG, format=FORMAT,
  datefmt=DATEFMT,
  filename=log,
  filemode='a')
consoleLog = logging.StreamHandler()
consoleLog.setLevel(logging.INFO)
consoleLog.setFormatter(logging.Formatter(FORMAT, DATEFMT))
logging.getLogger('').addHandler(consoleLog)
HEADER = '\x1b[95m'
OKCYAN = '\x1b[96m'
OKBLUE = '\x1b[94m'
OKGREEN = '\x1b[92m'
WARNING = '\x1b[93m'
FAIL = '\x1b[91m'
ENDC = '\x1b[0m'


def info(msg):
    logging.info(msg)


def Cpass(msg):
    logging.info('{0} {1} {2}'.format(OKGREEN, msg, ENDC))


def Ctime(msg):
    logging.info('{0} {1} {2}'.format(OKBLUE, msg, ENDC))


def Cfail(msg):
    logging.info('{0} {1} {2}'.format(FAIL, msg, ENDC))


def summary(msg):
    logging.info('{0} {1} {2}'.format(OKCYAN, msg, ENDC))


def debug(msg):
    logging.debug(msg)


def error(msg):
    logging.error('{0} {1} {2}'.format(FAIL, msg, ENDC))


def errorExit(msg):
    logging.error('{0} {1} {2}'.format(FAIL, msg, ENDC))


def title(task):
    logging.info('{0} {1} {2}'.format(OKCYAN, '======================================================================', ENDC))
    logging.info(' \t******\t\t {0} \t******\t'.format(task))
    logging.info('{0} {1} {2}'.format(OKCYAN, '======================================================================', ENDC))


def header(name):
    logging.info('')
    logging.info('{0} {1} {2}'.format(OKBLUE, '**********************************************************************', ENDC))
    logging.info('{0} {1} {2}'.format(OKBLUE, '*                                                            *', ENDC))
    logging.info('{0} {1} {2}'.format(OKBLUE, ' \t******\t{0}     ******\t'.format(name), ENDC))
    logging.info('')
    logging.info('{0} {1} {2}'.format(OKBLUE, '\t \tVersion : {0}'.format(scriptVersion), ENDC))
    logging.info('{0} {1} {2}'.format(OKBLUE, '\t \tAuthor : {0}'.format(author), ENDC))
    logging.info('{0} {1} {2}'.format(OKBLUE, '\t \tContact : {0}'.format(tel), ENDC))
    logging.info('{0} {1} {2}'.format(OKBLUE, '*                                                            *', ENDC))
    logging.info('{0} {1} {2}'.format(OKBLUE, '**********************************************************************', ENDC))
    logging.info('')

