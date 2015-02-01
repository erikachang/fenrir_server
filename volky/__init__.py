import logging
import os
import errno

logger = logging.getLogger('volky')
logFilePath = '/var/tmp/volky/'
logFileName = 'volky.log'


def make_log_dir():
    try:
        os.makedirs(logFilePath)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(logFilePath):
            pass
        else:
            raise

try:
    hdlr = logging.FileHandler(logFilePath+logFileName)
except IOError:
    make_log_dir()
    hdlr = logging.FileHandler(logFilePath+logFileName)

formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.DEBUG)
