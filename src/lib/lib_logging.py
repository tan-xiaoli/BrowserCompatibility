#!/usr/bin/env python
# coding=utf-8

import sys
import os

reload(sys)
sys.setdefaultencoding('utf8')

import logging
# from celery.utils.log import get_task_logger
from logging.handlers import TimedRotatingFileHandler

# Returns abs path relative to this file and not cwd
PATH = lambda p: os.path.abspath(
    os.path.join(os.path.dirname(__file__), p)
)

# 默认日志格式
logging.basicConfig(level=logging.DEBUG,
                    format='%(levelname)s\t%(asctime)s\t[%(filename)s:%(lineno)d]\t%(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename=PATH('../log/run.log'),
                    filemode='a')

global logger
logger = logging.getLogger(__file__)
# logger = get_task_logger('server')

# 定义一个流处理器StreamHandler，将INFO及以上日子打印到标准错误（stream_handler输出）
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)s\t%(asctime)s\t[%(filename)s:%(lineno)d]\t%(message)s',
                              '%Y-%m-%d %H:%M:%S')
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

# 定义一个文件处理器handler,将DEBUG日志打印到文件中
# file_hanlder = logging.FileHandler(filename=PATH('../log/run.log'), encoding='utf8')
# file_hanlder.setLevel(logging.DEBUG)
# formatter = logging.Formatter('%(levelname)s\t%(asctime)s\t[%(filename)s:%(lineno)d]\t%(message)s',
#                               '%Y-%m-%d %H:%M:%S')
# file_hanlder.setFormatter(formatter)
# logger.addHandler(file_hanlder)

# 按时间切分的TimeRotatingFileHandler
rotate_handler = TimedRotatingFileHandler(filename=PATH('../log/info.log'), when='midnight', interval=1, backupCount=10)
rotate_handler.setLevel(logging.INFO)
rotate_handler.suffix = '%Y%m%d.log'
formatter = logging.Formatter('%(levelname)s\t%(asctime)s\t[%(filename)s:%(lineno)d]\t%(message)s',
                              '%Y-%m-%d %H:%M:%S')
rotate_handler.setFormatter(formatter)
logger.addHandler(rotate_handler)


def get_logger():
    return logger
