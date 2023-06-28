# -*- encoding: utf-8 -*-
'''
@File    :   wheat_change.py
@Time    :   2023/03/29 15:53:03
@Author  :   HMX
@Version :   1.0
@Contact :   kzdhb8023@163.com
'''

# here put the import lib
from osgeo import gdal
import numpy as np

"""
需要注意在进行像素对齐时，不要更改上一年的数据！
"""

def tif2arr(tif):
    ds = gdal.Open(tif)
    return ds.ReadAsArray()

def get_change(lasttif,nowtif,outtif,gridvalues = 107):
    arr2 = tif2arr(lasttif).astype(np.int16)
    arr3 = tif2arr(nowtif).astype(np.int16)
    out1 = np.where((arr2!=gridvalues)&(arr3==gridvalues),1,0)#新增
    out2 = np.where((arr2==gridvalues)&(arr3!=gridvalues),2,0)#减少
    out3 = np.where((arr2==gridvalues)&(arr3==gridvalues),3,0)#不变
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


if __name__ == '__main__':
    w2 = r'E:\Project\潍坊项目\分类数据_v2\2022\wheat_2022_v4.tif'
    w3 = r'E:\Project\潍坊项目v2\种植结构变化\wheat_2023.tif'
    outtif = r'C:\Users\EDZ\Desktop\wheat_change_2023.tif'
    get_change(w2,w3,outtif)