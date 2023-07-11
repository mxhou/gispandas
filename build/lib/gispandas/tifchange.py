# -*- encoding: utf-8 -*-
'''
@File    :   种植结构变化.py
@Time    :   2023/06/26 10:21:18
@Author  :   HMX
@Version :   1.0
@Contact :   kzdhb8023@163.com
'''

# here put the import lib


"""
需要注意在进行像素对齐时，不要更改上一年的数据！
"""

import os
from osgeo import gdal
import numpy as np
import pandas as pd

def tif2arr(tif):
    '''读取栅格数据的数组

    :param tif: tif路径
    :return: tif数据的数组arr
    '''
    ds = gdal.Open(tif)
    return ds.ReadAsArray()

def tifchg(lasttif,nowtif,outtif,gridcode):
    '''种植结构变化

    :param lasttif: 去年的分类数据
    :param nowtif: 今年的分类数据
    :param outtif: 种植结果变化输出路径
    :param gridcode: 分类数据的作物代码
    '''
    last_arr = tif2arr(lasttif).astype(np.int16)
    now_arr = tif2arr(nowtif).astype(np.int16)
    out1 = np.where((last_arr!=gridcode)&(now_arr==gridcode),1,0)#新增
    out2 = np.where((last_arr==gridcode)&(now_arr!=gridcode),2,0)#减少
    out3 = np.where((last_arr==gridcode)&(now_arr==gridcode),3,0)#不变
    out = out1+out2+out3
    intif = gdal.Open(nowtif)
    nodata = 0
    # 创建输出文件并压缩
    driver = gdal.GetDriverByName('GTiff')
    dst_ds = driver.Create(outtif, out.shape[1], out.shape[0], 1, gdal.GDT_Byte, options=['COMPRESS=LZW'])
    dst_ds.SetProjection(intif.GetProjection())
    dst_ds.SetGeoTransform(intif.GetGeoTransform())
    dst_ds.GetRasterBand(1).WriteArray(out)
    dst_ds.GetRasterBand(1).SetNoDataValue(nodata)
    dst_ds = None
    intif = None
