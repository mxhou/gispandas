# -*- encoding: utf-8 -*-
'''
@File    :   tif2json.py
@Time    :   2023/03/31 16:04:48
@Author  :   HMX
@Version :   1.0
@Contact :   kzdhb8023@163.com
'''

# here put the import lib
import json
import time

import geopandas as gpd
import numpy as np
import rasterio
import rasterio.mask
from rasterio.warp import Resampling, calculate_default_transform, reproject
from rasterstats import zonal_stats


def tif2area(intif,inshp,class_dic,outjson,resolution=10,year=time.strftime('%Y'),code = 'code',name = 'name'):

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
    dx_re, dy_re = 10,10
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
