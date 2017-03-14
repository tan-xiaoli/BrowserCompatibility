#!/usr/bin/env python
# coding=utf-8

import sys

reload(sys)
sys.setdefaultencoding('utf8')

import os
import time
import hashlib
import functools
import inspect
import configobj
import urllib
import lib_logging

# Returns abs path relative to this file and not cwd
PATH = lambda p: os.path.abspath(
    os.path.join(os.path.dirname(__file__), p)
)

config = configobj.ConfigObj(PATH('../config/config.cfg'), encoding='utf8')
debug = config['Settings']['DEBUG']


def show_elapsed_time(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.clock()
        func(*args, **kwargs)
        end_time = time.clock()
        func_args = inspect.getcallargs(func, *args, **kwargs)
        if debug == '1':
            lib_logging.logger.info(
                '<%s> method args <%s> uses %ds.' % (func.__name__, func_args, end_time - start_time))

    return wrapper


def get_loc_from_str(location_str):
    """
    从conf文件中读取location
    """
    location = dict()
    location['x'] = location_str[0].strip()
    location['y'] = location_str[1].strip()
    return location


def local_command(cmd):
    """
    执行本地命令行
    """
    os.system(cmd)
    # return subprocess.call(cmd)


def md5(str):
    """
    获取str的md5
    """
    m = hashlib.md5()
    m.update(str)
    return m.hexdigest()


def delete_file(file_name):
    """
    删除文件
    """
    os.remove(file_name)


def url_quote(url):
    return urllib.quote(url)


def split_str_by_step(string, step=1):
    result = list()
    while string:
        result.append(string[:step])
        string = string[step:]
    return result


def get_datetime():
    return time.strftime('%Y%m%d', time.localtime(time.time()))
