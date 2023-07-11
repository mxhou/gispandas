# -*- encoding: utf-8 -*-
'''
@File    :   mxgdal.py
@Time    :   2023/07/11 21:14:20
@Author  :   HMX
@Version :   1.0
@Contact :   kzdhb8023@163.com
'''

# here put the import lib
import os
from osgeo import osr, ogr, gdal, gdalconst

def aligntif(infile,outfile,reffile,methods = gdalconst.GRA_NearestNeighbour,nodata = 0):
    '''像素对齐

    :param infile: 待对齐的tif
    :type infile: string
    :param outfile: 对齐后的tif
    :type outfile: string
    :param reffile: 参考tif
    :type reffile: string
    :param methods:重采样方式
    :type methods: _type_, optional
    :param nodata: 无效值
    :type nodata: int, optional
    '''
    in_ds  = gdal.Open(infile, gdalconst.GA_ReadOnly)
    ref_ds = gdal.Open(reffile, gdalconst.GA_ReadOnly)
    in_proj = in_ds.GetProjection()
    ref_trans = ref_ds.GetGeoTransform()
    ref_proj = ref_ds.GetProjection()
    x = ref_ds.RasterXSize
    y = ref_ds.RasterYSize
    driver= gdal.GetDriverByName('GTiff')
    output = driver.Create(outfile, x, y, 1, in_ds.GetRasterBand(1).DataType, options=['COMPRESS=LZW'])
    output.SetGeoTransform(ref_trans)
    output.SetProjection(ref_proj)
    output.GetRasterBand(1).SetNoDataValue(nodata)
    gdal.ReprojectImage(in_ds, output, in_proj, ref_proj, methods)
    in_ds = None
    ref_ds = None
    driver  = None
    output = None


def gdalmask(outtif,intif,shpfp):
    '''按掩膜提取栅格数据

    :param outtif: 裁剪后tif文件
    :param intif: 待裁剪的tif文件
    :param shpfp: 裁剪的矢量文件
    '''
    ds = gdal.Warp(
    outtif, 
    intif, 
    format='GTiff', 
    cutlineDSName=shpfp, 
    cropToCutline=True,
    dstNodata=0,
    outputType=gdal.GDT_Byte,
    options=['COMPRESS=LZW']
    )



def shp2tif(shapefile, rasterfile, savefile):
    """
    面转栅格TIF
    :param shapefile: 文件矢量Shapefile文件
    :param rasterfile: 栅格参照文件
    :param savefile: 文件输出路径
    """
    data = gdal.Open(rasterfile, gdal.GA_ReadOnly)
    x_res = data.RasterXSize
    y_res = data.RasterYSize
    shape = ogr.Open(shapefile)
    layer = shape.GetLayer()
    targetDataset = gdal.GetDriverByName('GTiff').Create(savefile, x_res, y_res, 1, gdal.GDT_Float32)
    targetDataset.SetGeoTransform(data.GetGeoTransform())
    targetDataset.SetProjection(data.GetProjection())
    band = targetDataset.GetRasterBand(1)
    band.SetNoDataValue(-9999)
    band.FlushCache()
    gdal.RasterizeLayer(targetDataset, [1, 2, 3], layer)


def tif2shp(rasterfile, shapefile):
    """
    栅格TIF转面
    :param rasterfile: 栅格TIF输入文件
    :param shapefile: 文件输出路径-矢量Shapefile文件
    :return:
    """
    data = gdal.Open(rasterfile, gdal.GA_ReadOnly)
    inband = data.GetRasterBand(1)
    drv = ogr.GetDriverByName('ESRI Shapefile')
    polygon = drv.CreateDataSource(shapefile)
    prj = osr.SpatialReference()
    prj.ImportFromWkt(data.GetProjection())  ## 使用栅格的投影信息
    polygon_layer = polygon.CreateLayer(shapefile, srs=prj, geom_type=ogr.wkbMultiPolygon)
    newField = ogr.FieldDefn('Value', ogr.OFTInteger)
    polygon_layer.CreateField(newField)
    gdal.FPolygonize(inband, None, polygon_layer, 0)