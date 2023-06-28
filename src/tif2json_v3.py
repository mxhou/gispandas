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



def main(intif,inshp,tempfp,class_dic,outjson):
    outtif,outshp = projtif(intif,inshp,tempfp)
    calculate_tif_area(outtif,outshp,class_dic,outjson)
    return outjson

if __name__ == '__main__':
    t1 = time.time()
    intif = r'E:\Project\潍坊项目v2\估产\估产v2\outdata\out\wheat_2023.tif'
    inshp = r'E:\Project\潍坊项目\客户边界v3\all\WF_city_county2000.geojson'
    tempfp = r'C:\Users\EDZ\Desktop\分类v2temp'
    class_dic = {"wheat": 107}
    outjson = r'C:\Users\EDZ\Desktop\分类v2temp\wheat23.json'
    main(intif,inshp,tempfp,class_dic,outjson)
    t2 = time.time()
    print('共计用时{:.2f}s'.format(t2 -t1))


    df = pd.read_json(outjson)
    print(df)