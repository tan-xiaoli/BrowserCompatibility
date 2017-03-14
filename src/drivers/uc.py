#!/usr/bin/env python
# coding=utf-8

########################################
#
# UC浏览器通用API
#
########################################

import sys
import os

reload(sys)
sys.setdefaultencoding('utf8')
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import time
import traceback
from appium import webdriver
from configobj import ConfigObj
from lib import lib_driver
from lib import lib_tools
from lib import lib_img
from lib import lib_redis
from lib import lib_logging
from lib import lib_upload
from lib.lib_driver import find_element_by_class_name_and_location as find_ele_by_cnl

# Returns abs path relative to this file and not cwd
PATH = lambda p: os.path.abspath(
    os.path.join(os.path.dirname(__file__), p)
)


class UC(object):

    def __init__(self, device):
        self.user = ''  # 用户名
        self.device = device  # 设备名称
        self.browser = 'UC'  # 浏览器名

        self.wait_time = 3
        self.loadpage_time = 5
        self.logger = lib_logging.get_logger()
        self.conf = ConfigObj(PATH('../config/config.cfg'), encoding='utf8')
        self.version_conf = ConfigObj(PATH('../config/version.cfg'), encoding='utf8')
        self.active_url_loc = lib_tools.get_loc_from_str(self.conf[self.device]['UC']['active_url_location'])
        self.url_loc = lib_tools.get_loc_from_str(self.conf[self.device]['UC']['url_location'])
        self.bottom_homepage_loc = lib_tools.get_loc_from_str(self.conf[self.device]['UC']['bottom_homepage_location'])
        self.bottom_settings_loc = lib_tools.get_loc_from_str(
            self.conf[self.device]['UC']['bottom_settings_location'])  # 屏幕下方设置按钮
        self.adblock_loc = lib_tools.get_loc_from_str(self.conf[self.device]['UC']['adblock_location'])  # 广告过滤
        self.cloud_accelerator_loc = lib_tools.get_loc_from_str(
            self.conf[self.device]['UC']['cloud_accelerator_location'])  # 云端加速
        self.version_loc = lib_tools.get_loc_from_str(self.conf[self.device]['UC']['version_location'])  # 版本号

        # --------------------Appium设置-------------------------------
        desired_cap = dict()
        desired_cap['automationName'] = 'appium'  # 自动化测试引擎
        desired_cap['platformName'] = self.conf[self.device]['platformName']  # 操作系统
        desired_cap['platformVersion'] = self.conf[self.device]['platformVersion']  # 系统版本
        desired_cap['udid'] = self.conf[self.device]['deviceName']
        desired_cap['deviceName'] = self.conf[self.device]['deviceName']  # 手机类型，android暂不起作用
        # desired_cap['newCommandTimeOut'] = 10  # 命令超时时间
        desired_cap['unicodeKeyboard'] = True  # 不使用键盘，用unicode发送文本
        desired_cap['resetKeyboard'] = True
        # desired_cap['app'] = PATH('UCBrowser.apk')  # 待测apk路径
        desired_cap['appPackage'] = 'com.UCMobile'
        desired_cap['appActivity'] = '.main.UCMobile'  # 启动的activity
        # 启动后等待的activity
        desired_cap['appWaitActivity'] = 'com.uc.browser.InnerUCMobile'
        self.driver = webdriver.Remote('http://127.0.0.1:%s/wd/hub' % self.conf[self.device]['listenPort'], desired_cap)
        self.device_window_size = self.driver.get_window_size()

    def __delete__(self):
        self.driver.close_app()
        self.driver.quit()

    def log_and_pub(self, msg=''):
        self.logger.debug('[%s]\t[%s]\t[%s]\t%s' % (self.user, self.device, self.browser, msg))
        lib_redis.send_msg('[%s]\t[%s]\t[%s]\t%s' % (self.user, self.device, self.browser, msg))

    def _go_to_homepage(self):
        """
        回到主页
        """
        self.log_and_pub('Go to home page...')
        if self._is_home_page():
            return
        homepage_btn = find_ele_by_cnl(self.driver, 'android.widget.ImageView', location=self.bottom_homepage_loc)
        homepage_btn.click()
        if self._is_home_page():
            return
        homepage_btn = find_ele_by_cnl(self.driver, 'android.widget.ImageView', location=self.bottom_homepage_loc)
        homepage_btn.click()

    def _active_url(self):
        """
        激活进入输入网址页面
        """
        self.log_and_pub('Active url input element...')
        self._go_to_homepage()
        self.driver.wait_activity('com.uc.browser.InnerUCMobile', 10, 2)
        active_url = find_ele_by_cnl(
            self.driver, 'android.view.View', location=self.active_url_loc)
        active_url.click()

    def _go_to_more_settings(self):
        """
        进入更多设置
        """
        self.log_and_pub('Go to more settings...')
        self._go_to_homepage()
        bottom_settings_iv = find_ele_by_cnl(self.driver, 'android.widget.ImageView', location=self.bottom_settings_loc)
        bottom_settings_iv.click()
        self.driver.find_element_by_name('设置').click()
        self.driver.find_element_by_name('更多').click()

    def _send_key_back(self):
        """
        模拟点击返回键
        """
        self.driver.keyevent(4)

    def _refresh_page(self):
        """
        刷新页面
        """
        self.log_and_pub('Refresh page...')
        bottom_settings_iv = find_ele_by_cnl(self.driver, 'android.widget.ImageView', location=self.bottom_settings_loc)
        bottom_settings_iv.click()
        self.driver.find_element_by_name('刷新').click()

    def _is_home_page(self):
        """
        检查是否是主页，通过查找页面中是否有 网址、小说、视频、奇趣、生活的viewgroup
        """
        five_small_dragon_loc = lib_tools.get_loc_from_str(self.conf[self.device]['UC']['five_small_dragon_location'])
        five_small_dragon = find_ele_by_cnl(self.driver, 'android.view.ViewGroup', location=five_small_dragon_loc)
        if five_small_dragon:
            return True
        return False

    def _open_link(self, link):
        """
        打开一个链接
        """
        self.driver.wait_activity('com.uc.browser.InnerUCMobile', 10, 2)
        self._go_to_homepage()
        self.driver.wait_activity('com.uc.browser.InnerUCMobile', 10, 2)
        self._active_url()
        url = find_ele_by_cnl(self.driver, 'android.view.View', location=self.url_loc)
        url.click()  # 使输入url获取焦点
        lib_driver.input_content(self.conf[self.device]['deviceName'], link)
        time.sleep(self.loadpage_time)

    def _close_pop_tools(self):
        try:
            pop_tools_tip = self.driver.find_element_by_name('选择复制')
            if pop_tools_tip:
                self._send_key_back()
        except:
            return None

    def _save_screenshot(self, file_name):
        """
        截图并保存
        """
        self.driver.get_screenshot_as_file(file_name)

    def _screenshot(self, pid='', file_path='', file_name='', browser='uc', scroll_time=1):
        """
        截图
        """
        self.log_and_pub('Screenshot...')
        files = list()
        for t in range(scroll_time):
            _file = os.path.join(file_path, '%s_%d.png' % (file_name, t))
            files.append(_file)
            self._save_screenshot(file_name=_file)
            lib_driver.page_dowm(self.driver, self.device_window_size)
            self._close_pop_tools()
        final_file = os.path.join(file_path, '%s-%s-%s-%s.png' % (self.device, browser, pid, file_name))
        lib_img.merge_img(final_file, files)
        for f in files:
            lib_tools.delete_file(f)
        return final_file

    def _upload_img(self, pid='', pid_name='', user='', img_file='', link='', browser='', device='', scroll_time=5):
        """
        上传图片
        """
        self.log_and_pub('Upload the imgage %s...' % img_file)
        if pid == 'real_monitor' and pid_name == 'real_monitor':
            upload_path = 'realtime/%s/' % user
        else:
            upload_path = 'regular/%s/%s/' % (user, lib_tools.get_datetime())
        ret, uploaded_img = lib_upload.upload_img(img_file, upload_path)
        if ret == -1:
            self.logger.error('Upload %s to CDN failed!' % img_file)
            return -1
        task_info = dict()
        task_info['pid'] = pid
        task_info['pid_name'] = pid_name
        task_info['user'] = user
        task_info['link'] = link
        task_info['browser'] = 2
        task_info['scroll_time'] = scroll_time
        task_info['uploaded_img'] = uploaded_img
        task_info['device'] = device
        lib_redis.send_task_done(task_info)

    @lib_tools.show_elapsed_time
    def restore_settings(self):
        """
        恢复默认设置
        """
        self.log_and_pub('Restore settings...')
        self._go_to_more_settings()
        lib_driver.scroll(self.driver, self.driver.find_element_by_name('WiFi助手'),
                          self.driver.find_element_by_name('下载设置'))
        self.driver.find_element_by_name('恢复默认').click()
        self.driver.find_element_by_name('恢复').click()
        self._send_key_back()
        self.log_and_pub('Restore settings for UC browser successfully!')

    @lib_tools.show_elapsed_time
    def check_update(self):
        """
        检查浏览器更新
        """
        self.log_and_pub('Check upadte...')
        self._go_to_more_settings()
        lib_driver.scroll(self.driver, self.driver.find_element_by_name('WiFi助手'),
                          self.driver.find_element_by_name('下载设置'))
        self.driver.find_element_by_name('检查更新').click()
        is_latest = self.driver.page_source.find('UC已是最新版本')
        if is_latest:
            self.log_and_pub('No need for update as it\'s the latest!')
            self._send_key_back()
        else:
            self.log_and_pub('Start update...')
            self.driver.find_element_by_name('立即更新').click()
            self.driver.wait_activity('com.android.packageinstaller', 10, 2)
            self.driver.find_element_by_name('安装').click()
            while True:
                is_finished = self.driver.page_source.find('应用安装完成。')
                if is_finished:
                    self.log_and_pub('Update successfully!')
                    return
                time.sleep(3)

    @lib_tools.show_elapsed_time
    def get_version(self):
        """
        获取浏览器版本
        """
        self.log_and_pub('Get version...')
        self._go_to_more_settings()
        lib_driver.scroll(self.driver, self.driver.find_element_by_name('WiFi助手'),
                          self.driver.find_element_by_name('下载设置'))
        version_tv = find_ele_by_cnl(self.driver, 'android.widget.TextView', location=self.version_loc)  # 版本号
        self.log_and_pub('The current version is %s.' % version_tv.text.split(' ')[1])
        version = version_tv.text.split(' ')[1]
        self.version_conf[self.device]['UC']['version'] = version
        self.version_conf.write()
        self._send_key_back()

    @lib_tools.show_elapsed_time
    def change_adblock(self, open=True):
        """
        更改广告拦截
        """
        self.log_and_pub('Change adblock...')
        self._go_to_more_settings()
        adblock = find_ele_by_cnl(
            self.driver, 'android.widget.ImageView', location=self.adblock_loc)  # 广告过滤
        if adblock.is_selected() is not open:
            adblock.click()
            self.log_and_pub('修改UC浏览器广告过滤状态，打开广告过滤！' if open else '修改UC浏览器广告过滤状态，关闭广告过滤！')
        else:
            self.log_and_pub('无需修改UC浏览器广告过滤状态，当前为打开广告过滤。' if open else '无需修改UC浏览器广告过滤状态，当前为关闭广告过滤。')
        self._send_key_back()

    @lib_tools.show_elapsed_time
    def change_cloud_accelerator(self, open=True):
        """
        更改云端加速
        """
        self.log_and_pub('Change clound accelerator...')
        self._go_to_more_settings()
        self.driver.find_element_by_name('极速/省流').click()
        cloud_accelerator = find_ele_by_cnl(self.driver, 'android.widget.ImageView',
                                            location=self.cloud_accelerator_loc)  # 云端加速
        if cloud_accelerator.is_selected() is not open:
            cloud_accelerator.click()
            self.log_and_pub('修改UC浏览器云端加速状态，打开云端加速！' if open else '修改UC浏览器云端加速状态，关闭云端加速！')
        else:
            self.log_and_pub('无需修改UC浏览器云端加速状态，当前为打开云端加速。' if open else '无需修改UC浏览器云端加速状态，当前为关闭云端加速。')
        self._send_key_back()
        self._send_key_back()

    @lib_tools.show_elapsed_time
    def browse(self, pid_name='', pid='', link='', browser='uc', user='', device='', scroll_time=5):
        self.user = user
        self.log_and_pub('Browse %s...' % link)
        start_time = time.time()
        try:
            self._open_link(link=link)
            name = lib_tools.md5(link)  # 以md5作为merged图片名
            final_file = self._screenshot(pid=pid, file_path=PATH('../screenshot/'),
                                          file_name=name, scroll_time=scroll_time)
            self._upload_img(pid=pid, pid_name=pid_name, user=user, img_file=final_file, link=link, browser=browser,
                             device=device, scroll_time=scroll_time)
        except:
            self.log_and_pub('Fail to browser [%s\t%s\t%s\t%s\t%s]. Error: %s' %
                             (device, 'UC', pid_name, pid, link, traceback.print_exc()))
            return
        end_time = time.time()
        self.log_and_pub('End browse %s. Total tasks %ds.' % (link, end_time - start_time))


def test():
    """
    测试
    """
    # uc = UC('XIAOMI_3')
    uc = UC('HUAWEI_Mate_8')

    links = ({
        'pid_name': 'real_monitor',
        'pid': 'real_monitor',
        'link': (
            # 'httpreal_img://inews.ifeng.com/50095508/news.shtml?ch=zbs_sogou_push&pushid=6&cid=951c47f6fe2fdae1ef94141fe97e77f2',
            'http://i.ifeng.com/?ch=ifengweb_2014',),
        'browser': '2',  # browser 2: UC
        'user': 'tanxiaoli',
        'device': '2',  # device 1: xiaomi 3 , 2: huawei
        'scroll_time': 5},
    )
    for item in links:
        for link in item['link']:
            uc.browse(item['pid_name'], item['pid'], link, item['browser'],
                      item['user'], item['device'], item['scroll_time'])
    print 'End the script!'

if __name__ == '__main__':
    test()
