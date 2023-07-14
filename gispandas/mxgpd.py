# -*- encoding: utf-8 -*-
'''
@File    :   shpinfo.py
@Time    :   2023/02/07 15:12:20
@Author  :   HMX 
@Version :   1.0
@Contact :   kzdhb8023@163.com
'''
# here put the import lib
import geopandas as gpd
import os
import warnings
import pandas as pd
from shapely import geometry
warnings.filterwarnings('ignore')

def shpinfo(shp,outshp=None):
    '''写入矢量数据的四至和中心经纬度

    :param shp: 待计算的矢量文件路径
    :param outshp:计算后的输出文件路径, defaults to None
    '''
    gdf = gpd.read_file(shp,engine = 'pyogrio')
    gdf['lon'] = gdf.centroid.x
    gdf['lat'] = gdf.centroid.y
    gdf[gdf['geometry'].bounds.columns.values] = gdf['geometry'].bounds
    if outshp is None:
        outshp = os.path.splitext(shp)[0]+'_out'+os.path.splitext(shp)[-1]
    gdf.to_file(outshp,encoding = 'utf-8')

def txt2shp(txtpath,shppath,lon,lat,EPSG=4490): 
    '''文本数据转矢量数据

    :param txtpath: 文本文件路径
    :param shppath: 输出的矢量文件路径
    :param lon: 经度字段名
    :param lat: 纬度字段名
    :param EPSG: 坐标系代码, defaults to 4490
    '''
    df = pd.read_csv(txtpath,header=0)
    print(df)
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df[lon], df[lat])
    ,crs = "EPSG:%S"%EPSG)
    # ds = gpd.read_file(shppath)
    # clipgdf = gpd.clip(gdf,ds)
    gdf.to_file(shppath)
    return

def boxshp(x1,x2,y1,y2,EPSG=4490):
    '''根据四至新建矩形矢量

    :param x1: xmin
    :param x2: xmax
    :param y1: ymin
    :param y2: ymax
    :param EPSG: 坐标系代码, defaults to 4490
    :return: gdf
    '''
    gdf = gpd.GeoSeries([geometry.Polygon([(x1, y1), (x1,y2), (x2, y2), (x2,y1)])],
                         crs="EPSG:%S"%EPSG
                         )
    return gdf

def clipshp(shp,clipshp,outshp):
    '''裁剪矢量

    :param shp: 待裁剪的矢量
    :param clipshp: 用于裁剪的矢量
    :param outshp: 裁剪后矢量
    '''
    res = gpd.read_file(shp).clip(clipshp)
    res.to_file(outshp)

def smoothshp(fn,outshp,EPSG=4326):
    '''矢量简化并投影,主要用于哨兵影像查询时简化

    :param fn: 待简化的矢量
    :param outshp: 简化后的矢量
    :param EPSG: 投影的坐标系代码, defaults to 4326
    '''
    gdf = gpd.read_file(fn).to_crs(f'EPSG:{EPSG}')
    gdf['geometry'] = gdf['geometry'].simplify(tolerance=0.1, preserve_topology=False)
    gdf.to_file(outshp,encoding='utf-8')


def projshp(shp,outshp,EPSG = 4490):
    '''投影矢量

    :param shp: 待投影矢量路径
    :param outshp: 投影后矢量路径
    '''
    gdf = gpd.read_file(shp).to_crs(f'EPSG:{EPSG}')
    gdf.to_file(outshp)