#!/usr/bin/env python
# coding=utf-8

import sys

reload(sys)
sys.setdefaultencoding('utf8')

import lib_logging
import numpy as np
from PIL import Image

logger = lib_logging.get_logger()


def merge_img(merged_name, imgs):
    """
    把多张图片合并为一张
    """
    for i, img in enumerate(imgs):
        if i == 0:
            base_img = Image.open(img)
            base_size = base_img.size
            base_mat = np.atleast_2d(base_img)
            continue
        _img = Image.open(img)
        _img = _img.resize(base_size, Image.ANTIALIAS)
        mat = np.atleast_2d(_img)
        base_mat = np.append(base_mat, mat, axis=0)
    final_img = Image.fromarray(base_mat)
    final_img.save(merged_name)
