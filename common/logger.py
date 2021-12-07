#-*- coding: utf-8 -*- 

import os
import logging

g_loggers = {}

def init_log():
    pass

def getLogger(name, level=logging.ERROR, filename=None):
    logger = g_loggers.get(name)
    if logger is not None:
        return logger

    logger = logging.getLogger(name)
    g_loggers[name] = logger

    logger.setLevel(level)
    fmt = logging.Formatter(
        "%(levelname)s|%(asctime)s|PID:%(process)d|TID:%(thread)d|%(filename)s|line:%(lineno)d|%(funcName)s|%(message)s",
        datefmt='%Y-%m-%d %H:%M:%S')
    if not filename:
        filename = name + ".log"

    logfile = os.path.join(".", "logs", filename)

    if os.path.exists(logfile):
        st = os.stat(logfile)
        if st.st_size >= 1024 * 1024 * 10:  # 10M
            try:
                os.remove(logfile)
            except:
                pass
    else:
        try:
            os.mkdir(os.path.dirname(logfile))
        except:
            pass
    fh = logging.FileHandler(logfile)
    fh.setFormatter(fmt)
    logger.handlers = []
    logger.addHandler(fh)

    debug = os.environ.get("debug")
    if debug:
        logger.setLevel(logging.DEBUG)
        fmt = logging.Formatter(
            "%(levelname)s|%(asctime)s|PID:%(process)d|TID:%(thread)d|%(filename)s|line:%(lineno)d|%(funcName)s|%(message)s",
            datefmt='%Y-%m-%d %H:%M:%S')
        ch = logging.StreamHandler()
        ch.setFormatter(fmt)
        logger.addHandler(ch)

    return logger