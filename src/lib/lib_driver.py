#!/usr/bin/env python
# coding=utf-8

import sys

reload(sys)
sys.setdefaultencoding('utf8')

import time
import traceback
import lib_logging
from appium.webdriver.common.touch_action import TouchAction
from lib_tools import local_command, split_str_by_step

logger = lib_logging.get_logger()


def find_element_by_class_name_and_location(driver, class_name='', location={}):
    """
    通过类名和坐标获取元素
    """
    items = driver.find_elements_by_class_name(class_name)
    try:
        for item in items:
            if str(item.location['x'])[:-2] == location['x'] and str(item.location['y'])[:-2] == location['y']:
                return item
    except:
        logger.error(traceback.print_exc())
        return None


def flick(driver, start_x, start_y, end_x, end_y):
    """
    实现快速滑动，appium元素的flick中使用的是press,无法实现快速滑动
    """
    action = TouchAction(driver)
    action.long_press(x=start_x, y=start_y, duration=50).move_to(x=end_x, y=end_y).release().perform()


def swipe(driver, start_x, start_y, end_x, end_y, duration=None):
    """
    实现带duration的滑动,appium元素的swipe中使用的是press,无法实现带duration的滑动
    """
    action = TouchAction(driver)
    action.long_press(x=start_x, y=start_y).wait(duration).move_to(x=end_x, y=end_y).release().perform()


def scroll(driver, start_el, end_el):
    """
    滑动,appium元素的scroll中使用的是press,无法实现滑动
    """
    action = TouchAction(driver)
    action.long_press(el=start_el).move_to(el=end_el).release().perform()


def scroll_left(driver, device_window_size):
    """
    向左滑动
    """
    width = device_window_size['width']
    height = device_window_size['height']
    flick(driver, start_x=width * 4 / 5, start_y=height / 2, end_x=width / 5, end_y=height / 2)


def scroll_right(driver, device_window_size):
    """
    向右滑动
    """
    width = device_window_size['width']
    height = device_window_size['height']
    flick(driver, start_x=width / 5, start_y=height / 2, end_x=width * 4 / 5, end_y=height / 2)


def scroll_down(driver, device_window_size):
    """
    向下滑动
    """
    width = device_window_size['width']
    height = device_window_size['height']
    flick(driver, start_x=width / 2, start_y=height * 3 / 4, end_x=width / 2, end_y=height / 4)


def scroll_up(driver, device_window_size):
    """
    向上滑动
    """
    width = device_window_size['width']
    height = device_window_size['height']
    flick(driver, start_x=width / 2, start_y=height / 4, end_x=width / 2, end_y=height * 3 / 4)


def page_dowm(driver, device_window_size):
    """
    向下翻页，一次scroll_up实现向下翻半页
    """
    scroll_down(driver, device_window_size)
    scroll_down(driver, device_window_size)


def page_up(driver, device_window_size):
    """
    向上翻页，一次scroll_down实现向上翻半页
    """
    scroll_up(driver, device_window_size)
    # time.sleep(1)
    scroll_up(driver, device_window_size)


def input_content_utf8(device, content):
    """
    通过adb向android输入文本
    此方法需要借助ADBKeyboard.apk，可通过adb shell的广告输入中文和英文
    """
    cmd = 'adb -s %s shell ime set com.android.adbkeyboard/.AdbIME 2>&1' % device  # 从ADB切换到ADBKeyBoard
    local_command(cmd)
    time.sleep(1)
    # 当输入字符串过长时，adb shell也无能为力，采取拆分字符串多次输入
    contents = split_str_by_step(content, 60)
    for item in contents:
        cmd = 'adb -s %s shell am broadcast -a ADB_INPUT_TEXT --es msg "%s"' % (device, item)  # 文本输入
        local_command(cmd)
        time.sleep(1)
    cmd = 'adb -s %s shell am broadcast -a ADB_EDITOR_CODE --ei code 2' % device  # 相当于回车
    local_command(cmd)


def input_content(device, content):
    """
    通过adb向android输入文本
    可通过adb shell的广告输入网址
    """
    # 当输入字符串过长时，adb shell也无能为力，采取拆分字符串多次输入
    contents = split_str_by_step(content, 60)
    for item in contents:
        cmd = 'adb -s %s shell input text "%s" 2>&1' % (device, item)  # 文本输入
        local_command(cmd)
        # time.sleep(1)
    cmd = 'adb -s %s shell input keyevent 66' % device  # 相当于回车
    local_command(cmd)


def click_enter(device):
    """
    模拟点击回车键
    """
    cmd = 'adb -s %s shell am broadcast -a ADB_EDITOR_CODE --ei code 2' % device  # 相当于回车
    local_command(cmd)
