# -*- coding: utf8 -*-

import os
import logging


LOG_FILE_FOLDER = "log"
LOG_FILE_NAME = "web_scrapy.log"
LOG_FILE_PATH = "%s/%s" % (LOG_FILE_FOLDER, LOG_FILE_NAME)


def reset_web_scrapy_logger_content(filename=LOG_FILE_PATH):
    if os.path.exists(filename):
        with open(filename, "w") as fp:
            fp.seek(0, 0)


def get_web_scrapy_logger(level=logging.DEBUG, filename=LOG_FILE_PATH):
# Create the folder for log file if it does NOT exist
    if not os.path.exists(LOG_FILE_FOLDER):
        os.makedirs(LOG_FILE_FOLDER)

    logging.basicConfig(filename=filename, level=level, format='%(asctime)-15s %(filename)s:%(lineno)d [%(levelname)s]: %(message)s')
# Log to console
    # console = logging.StreamHandler()
    # console.setLevel(logging.WARN)
    # console.setFormatter(logging.Formatter('%(asctime)-15s %(filename)s:%(lineno)d -- %(message)s'))
    # logging.getLogger().addHandler(console)
# Log to syslog
    from logging.handlers import SysLogHandler
    syslog = SysLogHandler(address='/dev/log')
    # syslog.setLevel(logging.INFO)
    syslog.setFormatter(logging.Formatter('%(filename)s:%(lineno)d [%(levelname)s]: %(message)s'))
    logging.getLogger().addHandler(syslog)

    return logging.getLogger();