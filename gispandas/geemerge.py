# -*- encoding: utf-8 -*-
'''
@File    :   影像镶嵌.py
@Time    :   2023/07/05 21:07:04
@Author  :   HMX
@Version :   1.0
@Contact :   kzdhb8023@163.com
'''

# here put the import lib
import numpy as np
from osgeo import gdal
import os
import time


def compress_tiff(intif, method="LZW") -> None:
    '''
    使用gdal,按照LZW方式压缩单张tiff
    LZW方法属于无损压缩，效果非常给力，4G大小的数据压缩后只有三十多M
    :param tiff: 原始tiff
    :param method: 压缩方式
    :return: None
    '''
    dataset = gdal.Open(intif)    
    driver = gdal.GetDriverByName('GTiff')
    outtif = intif.replace('.tif','_out.tif')
    driver.CreateCopy(outtif, dataset, strict=1, options=["TILED=YES", "COMPRESS={0}".format(method),'BIGTIFF=YES'])
    del dataset
    os.remove(intif)    
    os.rename(outtif, intif)


def merge_geetif(infp,outfp,lzw = True):
    '''镶嵌gee下载的栅格数据

    :param infp: 待镶嵌的栅格数据的文件夹路径
    :param outfp: 镶嵌后输出的文件夹路径_
    :param lzw: 是否压缩, defaults to True
    '''
    # 提取相同影像的flist
    flist = []
    iflist = []
    for f in os.listdir(infp):
        if f.endswith('.tif'):
            ifn = f.rsplit('-',1)[0].rsplit('-',1)[0]
            iflist.append(ifn)
            flist.append(os.path.join(infp, f)) 
    iflist = set(iflist)

    for ifn in iflist:
        outfs = []
        for fn in flist:
            if ifn in fn:
                outfs.append(fn)

        ds = gdal.Open(outfs[0])
        src = ds.GetProjection()
        outtif = os.path.join(outfp,ifn+'.tif')
        print(outtif)
        options =gdal.WarpOptions(srcSRS=src, dstSRS=src, format='GTiff', multithread=True, srcNodata=0
                                #   , creationOptions=['COMPRESS=LZW']
                                        )
        gdal.Warp(outtif, outfs, options=options)
        if lzw == True:
            compress_tiff(outtif, method="LZW")
