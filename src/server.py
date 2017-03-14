#!/usr/bin/env python
# coding=utf-8

import sys
import os

reload(sys)
sys.setdefaultencoding('utf8')

import json
import time
import threading
import multiprocessing
from Queue import Queue
from configobj import ConfigObj
from celery import Celery
from lib import lib_logging
from drivers.huawei import HUAWEI
from drivers.uc import UC
from drivers.xiaomi import XIAOMI

# Returns abs path relative to this file and not cwd
PATH = lambda p: os.path.abspath(
    os.path.join(os.path.dirname(__file__), p)
)

# logger
logger = lib_logging.get_logger()

# Celery Settings
conf = ConfigObj(PATH('./config/config.cfg'), encoding='utf8')
celery_broker_loc = conf['Settings']['CELERY_BROKER_LOC']
celery_app = Celery(broker='redis://' + celery_broker_loc + ':6379/1')
celery_app.conf.update(
    CELERY_SEND_TASK_SENT_EVNET=True,
    CELERY_SEND_EVENTS=True,
    CELERY_ACCEPT_CONTENT=['json'],
    CELERY_TASK_SERIALIZER='json',
    CELERY_TIMEZONE='Asia/Shanghai',
    CELERY_ENABLE_UTC=False,
    USE_TZ=True,
    TIME_ZONE='Asia/ShangHai',
    CELERY_RESULT_BACKEND='redis://' + celery_broker_loc + ':6379/1',
    CELERY_RESULT_SERIZLIZER='json',
    BROKER_TRANSPORT='redis',
)

# 设备使用信息
devices = {
    'XIAOMI_3': {'is_using': False},
    'HUAWEI_Mate_8': {'is_using': False},
    'OPPO_R7sm': {'is_using': False},
    'VIVO_X5': {'is_using': False}
}

# 分设备的任务队列
xiaomi_3_task_queue = Queue()
huawei_mate_8_task_queue = Queue()
oppo_r7sm_task_queue = Queue()
vivo_x5_task_queue = Queue()


def _check_device(device=''):
    """
    检查设备信息及当前设备的使用状态
    """
    if device not in devices.keys():
        logger.error('Device Name <"%s"> Error!' % device)
        return 0
    return 1


@celery_app.task(name='accept_request', trail=True)
def accept_request(req_params):
    logger.info('Accept request: %s' % req_params)
    params = json.loads(req_params)
    device = params['device']
    if device == '1':  # 小米3
        xiaomi_3_task_queue.put(req_params)
    elif device == '2':  # 华为Mate8
        huawei_mate_8_task_queue.put(req_params)


def _invoke_xiaomi_3(task=''):
    """
    调用小米3任务
    """
    global devices
    devices['XIAOMI_3']['is_using'] = True  # 设置设备使用状态

    task_info = json.loads(task)
    if task_info['browser'] == '1':  # 系统自带
        browser = XIAOMI('XIAOMI_3')
        task_info['browser'] = 'native'
    elif task_info['browser'] == '2':  # UC浏览器
        browser = UC('XIAOMI_3')
        task_info['browser'] = 'UC'
    else:
        return -1

    if task_info['method'] == 'browse':
        browser.browse(pid_name=task_info['pid_name'], pid=task_info['pid'], link=task_info['link'],
                       browser=task_info['browser'], scroll_time=task_info['scroll_time'], user=task_info['user'],
                       device=task_info['device'])
    elif task_info['method'] == 'restore_settings':
        browser.restore_settings()
    elif task_info['method'] == 'check_update':
        browser.check_update()
    elif task_info['method'] == 'get_version':
        browser.get_version()
    elif task_info['method'] == 'change_adblock':
        browser.change_adblock()
    elif task_info['method'] == 'change_cloud_accelerator' and task_info['browser'] == 'uc':
        browser.change_cloud_accelerator()

    devices['XIAOMI_3']['is_using'] = False


def _invoke_huawei_mate_8(task=''):
    """
    调用华为Mate 8任务
    """
    global devices
    devices['HUAWEI_Mate_8']['is_using'] = True  # 设置设备使用状态

    task_info = json.loads(task)
    if task_info['browser'] == '1':  # 系统自带
        browser = HUAWEI('HUAWEI_Mate_8')
        task_info['browser'] = 'native'
    elif task_info['browser'] == '2':  # UC浏览器
        browser = UC('HUAWEI_Mate_8')
        task_info['browser'] = 'UC'
    else:
        return -1

    if task_info['method'] == 'browse':
        browser.browse(pid_name=task_info['pid_name'], pid=task_info['pid'], link=task_info['link'],
                       browser=task_info['browser'], scroll_time=task_info['scroll_time'], user=task_info['user'],
                       device=task_info['device'])
    elif task_info['method'] == 'restore_settings':
        browser.restore_settings()
    elif task_info['method'] == 'check_update':
        browser.check_update()
    elif task_info['method'] == 'get_version':
        browser.get_version()
    elif task_info['method'] == 'change_adblock':
        browser.change_adblock()
    elif task_info['method'] == 'change_cloud_accelerator' and task_info['browser'] == 'uc':
        browser.change_cloud_accelerator()

    devices['HUAWEI_Mate_8']['is_using'] = False


def run_task():
    """
    后台执行任务
    """
    global devices
    while 1:
        if not xiaomi_3_task_queue.empty() and not devices['XIAOMI_3']['is_using']:
            task = xiaomi_3_task_queue.get()
            logger.info("XIAOMI 3 Task: %s." % task)
            t = threading.Thread(target=_invoke_xiaomi_3, args=(task,))
            t.setDaemon(True)
            t.start()
        if not huawei_mate_8_task_queue.empty() and not devices['HUAWEI_Mate_8']['is_using']:
            task = huawei_mate_8_task_queue.get()
            logger.info("HUAWEI Mate 8 Task: %s." % task)
            t = threading.Thread(target=_invoke_huawei_mate_8, args=(task,))
            t.setDaemon(True)
            t.start()
        time.sleep(1)


if __name__ == '__main__':
    main_thread = threading.Thread(target=run_task)
    main_thread.setDaemon(True)
    main_thread.start()
