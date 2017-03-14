#!/usr/bin/env python
# coding=utf-8

import sys

reload(sys)
sys.setdefaultencoding('utf8')

import os
import urllib2
import traceback
import poster
import cookielib
from configobj import ConfigObj

# Returns abs path relative to this file and not cwd
PATH = lambda p: os.path.abspath(
    os.path.join(os.path.dirname(__file__), p)
)

conf = ConfigObj(PATH('../config/config.cfg'), encoding='utf8')
upload_url = conf['Settings']['UPLOAD_URL']
remote_path = conf['Settings']['REMOTE_PATH']


def upload_img(img_file, upload_path):
    """
    上传图片
    """
    params = {
        'file': open(img_file, 'rb'),
        'path': upload_path
    }
    try:
        opener = poster.streaminghttp.register_openers()
        opener.add_handler(urllib2.HTTPCookieProcessor(cookielib.CookieJar()))
        datagen, headers = poster.encode.multipart_encode(params)
        request = urllib2.Request(upload_url, datagen, headers)
        result = urllib2.urlopen(request)
        print result.read()
        return 0, '%s/%s/%s' % (remote_path, upload_path, os.path.basename(img_file))
    except:
        return -1, traceback.print_exc()
