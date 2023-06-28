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
import os
import time
import geopandas as gpd
from osgeo import gdal, osr
from rasterstats import zonal_stats
import pandas as pd
import sys
import shutil
import numpy as np


def projtif(intif,inshp,outfp,xres = 10,yres = 10):
    outtif = os.path.join(outfp,os.path.basename(intif).split('.')[0]+'_albert.tif')
    outshp = os.path.join(outfp,os.path.basename(inshp).split('.')[0]+'_albert.shp')
    # 创建Albers等面积投影对象
    spatial_ref = osr.SpatialReference()
    spatial_ref.ImportFromProj4("+proj=aea +lat_1=25 +lat_2=47 +lat_0=0 +lon_0=105 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs")
    
    gdal.Warp(outtif , # 输出栅格路径
            intif,  # 输入栅格
            format='GTiff',  # 导出tif格式
            dstSRS = spatial_ref, # 投影
            xRes=xres, # 重采样后的x方向分辨率
            yRes=yres, # 重采样后的y方向分辨率
            resampleAlg=gdal.GRA_NearestNeighbour, #最邻近重采样
            creationOptions=['COMPRESS=LZW']#lzw压缩栅格
            )
    ds = gdal.Open(outtif)
    crs = ds.GetProjection()    
    gdf = gpd.read_file(inshp,engine='pyogrio')
    gdf.to_crs(crs,inplace=True)
    gdf.to_file(outshp,encoding = 'utf-8')
    ds = None
    return outtif,outshp



def calculate_tif_area(outtif,outshp,class_dic,outjson,year=time.strftime('%Y')):
    # 读取tif信息
    ds = gdal.Open(outtif)
    nodata = ds.ReadAsArray()[0,0]
    dx_re, dy_re = ds.GetGeoTransform()[1], ds.GetGeoTransform()[-1]
    # 读取分类信息
    ks = list(class_dic.keys())
    vs = list(class_dic.values())
    # 统计栅格数量
    stats = zonal_stats(outshp, outtif
    , stats=" mean count"
    , nodata=nodata
    , categorical=True
    , category_map=class_dic
    , geojson_out=True
    )

    # 写入json文件
    item_list = []            
    for v in range(len(ks)):                       
        for t in stats:
            data = {}
            code = t.get('properties').get('code')
            name = t.get('properties').get('name')
            data['code'] = code
            data['name'] = name
            data['year'] = year
            data['type'] = str(ks[v])
            if t.get('properties').get(vs[v]) is None:
                data['area'] = 0.
            else:
                data['area'] = round(
                    t.get('properties').get(vs[v]) * (abs(dx_re* dy_re) *0.0015), 2)
            item_list.append(data)
    
    with open(outjson, 'w',encoding = 'utf-8') as fw:
        fw.write(json.dumps(item_list, ensure_ascii=False,indent=2))



def tif2area(intif,inshp,class_dic,outjson,tempfp=os.path.join(os.path.dirname(__file__), 'temp_tif2json'),isdel = 1):
    '''
    intif:待统计的tif数据
    inshp:待统计的shp数据
    class_dic:tif数据栅格值对应的属性名 字典类型
    outjson:统计后的数据文件
    tempfp:中间数据文件临时存储位置
    isdel:是否删除临时文件
    '''

    # 新建临时文件夹
    if not os.path.exists(tempfp):
        os.makedirs(tempfp)
    else:
        tempfp = os.path.join(os.path.dirname(__file__), f'temp_tif2json{str(np.random.randint(1,999999,1)[0]).zfill(10)}')
        os.makedirs(tempfp)
    # 投影栅格和矢量数据
    outtif,outshp = projtif(intif,inshp,tempfp)
    # 计算面积导出json
    calculate_tif_area(outtif,outshp,class_dic,outjson)
    # 判断是否删除临时文件
    if isdel==1:
        shutil.rmtree(tempfp)
    return outjson

def f1(temp = os.path.join(os.path.dirname(__file__), 'temp'),isdel = 1):
    if not os.path.exists(temp):
        os.makedirs(temp)
        
    else:
        temp = os.path.join(os.path.dirname(__file__), f'temp_{str(np.random.randint(1,999999,1)[0]).zfill(10)}')
        os.makedirs(temp)
    if isdel==1:
        shutil.rmtree(temp)
    print('del')


if __name__ == '__main__':
    t1 = time.time()
    intif = r'E:\Project\潍坊项目v2\估产\估产v2\outdata\out\wheat_2023.tif'
    inshp = r'E:\Project\潍坊项目v2\客户矢量v5\all\wf_all2000_info.geojson'
    class_dic = {"wheat": 107}
    outjson = r'E:\Project\custom function\wheat23.json'
    tif2area(intif,inshp,class_dic,outjson)
    t2 = time.time()
    print('共计用时{:.2f}s'.format(t2 -t1))
    df = pd.read_json(outjson)
    print(df)