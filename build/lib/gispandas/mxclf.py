# -*- encoding: utf-8 -*-
'''
@File    :   种植结构变化.py
@Time    :   2023/06/26 10:21:18
@Author  :   HMX
@Version :   1.0
@Contact :   kzdhb8023@163.com
'''

# here put the import lib




import json
import os
import time
from osgeo import gdal
import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
import rasterio.mask
from mxgdal import *
from rasterio.warp import Resampling, calculate_default_transform, reproject
from rasterstats import zonal_stats



def tif2area(intif,inshp,class_dic,outjson,resolution=10,year=time.strftime('%Y'),code = 'code',name = 'name'):
    '''根据矢量区划统计tif数据的面积

    :param intif: 待统计的栅格数据
    :param inshp: 待统计的矢量区划
    :param class_dic: 作物类别和栅格像元值例如{"wheat": 107,"corn": 102}
    :param outjson: 输出的统计json文件,注意导出的area单位默认为亩
    :param resolution: 分辨率, defaults to 10
    :param year: 数据年份, defaults to time.strftime('%Y')
    :param code: 矢量数据里行政区划代码的字段名称, defaults to 'code'
    :param name: 矢量数据里行政区划名称的字段名称, defaults to 'name'
    :return: 输出的统计json文件
    '''
    # 投影
    # 投影矢量
    dst_crs = '+proj=aea +lat_1=25 +lat_2=47 +lat_0=0 +lon_0=105 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs'
    gdf = gpd.read_file(inshp)
    gdf.to_crs(dst_crs,inplace=True)

    # 投影栅格
    with rasterio.open(intif) as src:
        profile = src.profile
        # 计算重投影后的栅格的分辨率和范围
        dst_transform, dst_width, dst_height = calculate_default_transform(
            src.crs, dst_crs, src.width, src.height, *src.bounds, resolution=resolution)
        # 更新栅格的元数据
        profile.update({
            'crs': dst_crs,
            'transform': dst_transform,
            'width': dst_width,
            'height': dst_height
        })
        # 创建新的重投影后的栅格文件
        dst_arr = np.zeros((dst_height, dst_width), dtype=src.dtypes[0])
        reproject(
            source=rasterio.band(src, 1),
            destination=dst_arr,
            src_transform=src.transform,
            src_crs=src.crs,
            dst_transform=dst_transform,
            dst_crs=dst_crs,
            resampling=Resampling.nearest
        )

    # 空间统计
    dx_re, dy_re = resolution,resolution
    ks = list(class_dic.keys())
    vs = list(class_dic.values())
    stats = zonal_stats(gdf, dst_arr
    , stats=" mean count"
    , nodata=src.nodata
    , categorical=True
    , category_map=class_dic
    , geojson_out=True
    ,affine=dst_transform
    )
    item_list = [ 
                {'code': t.get('properties').get(code),
                'name': t.get('properties').get(name),
                'year': year,
                'type': f'{k}',
                'area': round(
                t.get('properties').get(v) * (abs(dx_re* dy_re) *0.0015), 2) if t.get('properties').get(v) is not None else 0.
                }
                for k, v in zip(ks, vs)
                for t in stats
                ]

    # 写入json
    with open(outjson, 'w',encoding = 'utf-8') as fw:
        json.dump(item_list, fw, ensure_ascii=False,indent=2)
    return outjson


def tifchg(lasttif,nowtif,outtif,gridcode,nodata = 0):
    '''种植结构变化，需要注意在进行像素对齐时，不要更改上一年的数据！

    :param lasttif: 去年的分类数据
    :param nowtif: 今年的分类数据
    :param outtif: 种植结果变化输出路径，默认为1增2减3不变！！！
    :param gridcode: 分类数据的作物代码
    :param nodata: 栅格无效值, defaults to 0,不建议修改！！！
    '''
    
    last_arr = tif2arr(lasttif).astype(np.int16)
    now_arr = tif2arr(nowtif).astype(np.int16)
    out1 = np.where((last_arr!=gridcode)&(now_arr==gridcode),1,nodata)#新增
    out2 = np.where((last_arr==gridcode)&(now_arr!=gridcode),2,nodata)#减少
    out3 = np.where((last_arr==gridcode)&(now_arr==gridcode),3,nodata)#不变
    out = out1+out2+out3
    intif = gdal.Open(nowtif)
    # 创建输出文件并压缩
    driver = gdal.GetDriverByName('GTiff')
    dst_ds = driver.Create(outtif, out.shape[1], out.shape[0], 1, gdal.GDT_Byte, options=['COMPRESS=LZW'])
    dst_ds.SetProjection(intif.GetProjection())
    dst_ds.SetGeoTransform(intif.GetGeoTransform())
    dst_ds.GetRasterBand(1).WriteArray(out)
    dst_ds.GetRasterBand(1).SetNoDataValue(nodata*3)
    dst_ds = None
    intif = None


def cropchg(lasttif,nowtif,outtif,outjson,shpfp,gridcode,nodata = 0,resolution=10,year=time.strftime('%Y'),code = 'code',name = 'name'):
    '''作物种植结构一键导出tif和json

    :param lasttif: 去年的分类数据
    :param nowtif: 今年的分类数据
    :param outtif: 种植结构变化栅格数据
    :param outjson: 种植结构变化统计数据
    :param shpfp: 待统计的行政区划数据
    :param gridcode: 作物代码即，分类数据的像元值
    :param nodata: 种植结构栅格的无效值，非必要不要修改！！！ defaults to 0
    :param resolution: 栅格分辨率, defaults to 10
    :param year: 数据年份, defaults to time.strftime('%Y')
    :param code: 矢量数据行政区划代码的字段名, defaults to 'code'
    :param name: 矢量数据行政区划名称的字段名, defaults to 'name'
    '''
    nowtif_align = nowtif.replace('.tif','_align.tif')
    aligntif(nowtif,nowtif_align,lasttif)
    tifchg(lasttif,nowtif_align,outtif,gridcode,nodata = nodata)
    class_dic = {'increase':1,'decrease':2,'nochange':3}
    tif2area(outtif,shpfp,class_dic,outjson,resolution=resolution,year=year,code = code,name = name)
