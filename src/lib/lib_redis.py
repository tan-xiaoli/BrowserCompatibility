#!/usr/bin/env python
# coding=utf-8

import os
import sys

reload(sys)
sys.setdefaultencoding('utf8')

import redis
import json
from configobj import ConfigObj

# Returns abs path relative to this file and not cwd
PATH = lambda p: os.path.abspath(
    os.path.join(os.path.dirname(__file__), p)
)

# Redis Settings
conf = ConfigObj(PATH('../config/config.cfg'), encoding='utf8')
redis_loc = conf['Settings']['REDIS_LOC']
channel = conf['Settings']['REDIS_CHANNEL']
port = conf['Settings']['REDIS_PORT']


def send_msg(msg=''):
    """
    向redis发送json消息
    """
    if len(msg) == 0:
        return -1
    redis_instance = redis.StrictRedis(host=redis_loc, port=port)
    info = dict()
    info['message'] = msg
    redis_instance.publish(channel, json.dumps(info))
    redis_instance.connection_pool.disconnect()


def send_task_done(task_info={}):
    """
    向redis发送task done
    """
    if len(task_info) == 0:
        return -1
    redis_instance = redis.StrictRedis(host=redis_loc, port=port)
    info = dict()
    info['task_done'] = json.dumps(task_info)
    redis_instance.publish(channel, json.dumps(info))
    redis_instance.connection_pool.disconnect()
