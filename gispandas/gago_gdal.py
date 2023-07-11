#!/usr/bin/env python
# -*- coding: utf-8 -*-!
import os, sys
import glob
import numpy as np
import datetime
from osgeo import gdal,ogr,osr, gdalconst


def read_tiff_meta(intiff:str) -> list:
	'''
	读取栅格元数据元素
	:param intiff: 输入的栅格
	:return:
			xsize: 栅格水平空间大小
    		ysize: 栅格垂直空间大小
        	pixel_width: 像元水平空间分辨率
        	pixel_height: 像元垂直空间分辨率
        	originX: 影像左上角横坐标
        	originY: 影像左上角纵坐标
	'''
	gdal.UseExceptions()  # not required, but a good idea
	ds = gdal.Open(intiff, gdal.GA_ReadOnly)
	xsize=ds.RasterXSize
	ysize=ds.RasterYSize
	geotransform = ds.GetGeoTransform()
	originX, originY = geotransform[0], geotransform[3]
	pixel_width, pixel_height = geotransform[1], geotransform[5]
	return [xsize, ysize, pixel_width, pixel_height, originX, originY]


def readtiff(tiff:str) -> np.array:
	'''
	读入栅格文件，返回数组
	:param tiff: 读取的tiff文件
	:return: 二维数组
	'''
	gdal.UseExceptions()  # not required, but a good idea
	image = gdal.Open(tiff,gdal.GA_ReadOnly)
	band = image.GetRasterBand(1)
	array = band.ReadAsArray()
	return array


def write2tiff(var:np.array, max_lat:float, dx:float, min_lon:float, dy:float, data_type:str, nodata:int, coord_type:int, outtiff:str) ->None:
	'''
	写入tiff
	That's (top left x, w-e pixel resolution, rotation (0 if North is up), top left y, rotation (0 if North is up), n-s pixel resolution)
	GIS栅格通常在左上角注册世界坐标，并使用-dy值向下计数行，dx值想右计列。
	但是，大多数软件通常都可以使用带有+dy的左下角。当将数组作为打印矩阵与映射栅格进行比较时，它会倒置。
	:param var: 要素二维数组
	:param max_lat: 左上角纬度
	:param dx: 横向分辨率
	:param min_lon: 左上角经度
	:param dy: 纵向分辨率(<0)
	:param data_type: 数据类型（整型、浮点型）
	:param nodata: 自定义无效值
	:param coord_type: 投影坐标系
	:param outtiff: 输出tiff文件名
	:return: None
	'''
	if os.path.exists(outtiff):
		os.remove(outtiff)

	gdal.UseExceptions() # not required, but a good idea
	driver = gdal.GetDriverByName('GTiff')
	nlat,nlon  = var.shape[0],var.shape[1] # (180,360)

	if 'int' in data_type or "Int" in data_type or "INT" in data_type:
		out_raster = driver.Create(outtiff, nlon, nlat, 1, gdal.GDT_Int16)
	elif "float" in data_type or "Float" in data_type or "FLOAT" in data_type:
		out_raster = driver.Create(outtiff, nlon, nlat, 1, gdal.GDT_Float32)

	out_raster.SetGeoTransform((min_lon, dx, 0, max_lat, 0, dy))  # Specify its coordinates

	for i in range(0, 1):
		out_band = out_raster.GetRasterBand(i + 1)
		outRasterSRS = gdal.osr.SpatialReference() # Establish its coordinate encoding
		outRasterSRS.ImportFromEPSG(int(coord_type))  # This specifies coordinate system (4326/4490)
		out_raster.SetProjection(outRasterSRS.ExportToWkt()) # Exports the coordinate system to the file
		out_band.SetNoDataValue(nodata)
		out_band.WriteArray(var) # (360,180)
		out_band.FlushCache()


def write2shp(var:np.array, shp_type:str, coord:int) -> None:

	# 为了支持中文路径，请添加下面这句代码
	gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8","NO")
	# 为了使属性表字段支持中文，请添加下面这句
	gdal.SetConfigOption("SHAPE_ENCODING","")

	outshp = '.shp'
	# 注册所有的驱动
	ogr.RegisterAll()

	# 创建数据，这里以创建ESRI的shp文件为例
	DriverName = "ESRI Shapefile"
	oDriver = ogr.GetDriverByName(DriverName)

	if oDriver == None:
		return "驱动不可用："+DriverName
	# 创建数据源
	oDS = oDriver.CreateDataSource("polygon.shp")
	if oDS == None:
		return "创建文件失败 " + ".shp"

	# 创建一个点图层，指定坐标系为WGS84
	papszLCO = []
	geosrs = osr.SpatialReference()
	geosrs.ImportFromEPSG(coord)
	# geosrs.SetWellKnownGeogCS(coordinate[str(coord)])
	# 线：ogr_type = ogr.wkbLineString
	ogr_type = ogr.wkbPoint # 点
	# 多边形：ogr_type = ogr.wkbPolygon
	# 面的类型为Polygon，线的类型为Polyline，点的类型为Point
	oLayer = oDS.CreateLayer("Point", geosrs, ogr_type, papszLCO)
	if oLayer == None:
		return "图层创建失败！"
	# 创建属性表
	# 创建id字段
	oId = ogr.FieldDefn("id", ogr.OFTInteger)
	oLayer.CreateField(oId, 1)
	# 创建name字段
	oName = ogr.FieldDefn("name", ogr.OFTString)
	oLayer.CreateField(oName, 1)
	oDefn = oLayer.GetLayerDefn()


def Get4Points(shp_file:str) -> float:
	'''
	读取矢量文件的四至点坐标, type为矢量文件后缀名 shp或geojson
	:param shp_file: 传入的矢量文件(.geojosn，.shp)
	:return: 四至坐标点
	'''
	shp_ds = ogr.Open(shp_file,0) # 0是只读，1是可写
	layer = shp_ds.GetLayer()
	extent = layer.GetExtent()
	xmin, xmax, ymin, ymax = extent[0],extent[1],extent[2],extent[3]
	return xmin, ymin, xmax, ymax


def compress(origin_path:str, method="LZW") -> None:
	'''
	使用gdal,按照LZW方式压缩指定文件夹下所有tiff
	LZW方法属于无损压缩，效果非常给力，4G大小的数据压缩后只有三十多M
	:param origin_path: 原文件路径
	:param method: 压缩方式
	:return: None
	'''
	tiffs = sorted(glob.glob(origin_path + '*.tif*'))
	for tiff in tiffs:
		dataset = gdal.Open(tiff)
		os.remove(tiff)
		driver = gdal.GetDriverByName('GTiff')
		driver.CreateCopy(tiff, dataset, strict=1, options=["TILED=YES", "COMPRESS={0}".format(method)])
		del dataset


def compress_tiff(tiff:str, method="LZW") -> None:
	'''
	使用gdal,按照LZW方式压缩单张tiff
	LZW方法属于无损压缩，效果非常给力，4G大小的数据压缩后只有三十多M
	:param tiff: 原始tiff
	:param method: 压缩方式
	:return: None
	'''
	dataset = gdal.Open(tiff)
	os.remove(tiff)
	driver = gdal.GetDriverByName('GTiff')
	driver.CreateCopy(tiff, dataset, strict=1, options=["TILED=YES", "COMPRESS={0}".format(method)])
	del dataset


def tiff_fit(input_raster:str, fit_raster:str, out_raster:str) -> None:
	'''
	像素对齐
	:param input_raster: 未对齐影像
	:param fit_raster: 参考影像
	:param out_raster: 已对齐影像
	:return: None
	'''
	if os.path.exists(out_raster):
		os.remove(out_raster)
	fit_shape = readtiff(fit_raster).shape
	cmd = "gdalwarp -ts %s %s %s %s -r near" % (fit_shape[1], fit_shape[0], input_raster, out_raster)
	os.system(cmd)
	print('finish')


def transform_tiff(coord:int, intif:str, outtif:str) -> None:
	'''
	重投影
	:param coord: 投影坐标系
	:param intif: 转换投影前的栅格
	:param outtif: 转换投影后的栅格
	:return: None
	'''
	if os.path.exists(outtif):
		os.remove(outtif)
	cmd = 'gdalwarp -t_srs EPSG:%s %s %s' % (coord, intif, outtif)
	os.system(cmd)


def tiff_clip_orthogon(input_raster:str, xmin:float, ymin:float, xmax:float, ymax:float, out_raster:str) -> None:
	'''
	按照四至裁剪栅格
	:param input_raster: 传入的栅格
	:param xmin: 最小经度
	:param ymin: 最小纬度
	:param xmax: 最大经度
	:param ymax: 最大纬度
	:param out_raster: 裁剪后影像
	:return: None
	'''
	if os.path.exists(out_raster):
		os.remove(out_raster)
	cmd = 'gdalwarp -te %s %s %s %s %s %s' % (xmin, ymin, xmax, ymax, input_raster, out_raster)
	os.system(cmd)


def tiff_clip_border(input_raster:str, shp:str, nodata:int, out_raster:str) -> None:
	'''
	按照边界裁剪栅格
	:param input_raster: 传入的栅格
	:param shp: 传入的矢量边界(.shp或.geojson)
	:param nodata: 设置裁剪后影像无效值
	:param out_raster: 裁剪后影像
	:return: None
	'''
	if os.path.exists(out_raster):
		os.remove(out_raster)
	cmd = "gdalwarp --config GDAL_FILENAME_IS_UTF8 NO --config SHAPE_ENCODING UTF-8 \
			--config GDALWARP_IGNORE_BAD_CUTLINE YES \
			-cutline %s -srcnodata %s -crop_to_cutline %s %s"%(shp, str(nodata), input_raster, out_raster)
	os.system(cmd)
	# if os.path.exists(input_raster):
	# 	os.remove(input_raster)


def tiff_resample(input_raster: str, dx_re, dy_re, out_raster: str):
	'''
	栅格重采样
	:param input_raster: 传入的栅格
	:param dx_re: 经向分辨率
	:param dy_re: 纬向分辨率
	:param out_raster: 重采样后影像
	:return: None
	'''
	if os.path.exists(out_raster):
		os.remove(out_raster)
	cmd = "gdalwarp -r cubicspline -tr %s %s %s %s" % (dx_re, dy_re, input_raster, out_raster)
	os.system(cmd)


def tiff2lerc(input_path: str, min_level:int, max_level:int, coord:int, out_path: str) -> None:
	'''
	tiff转为lerc格式
	:param input_path: tiff路径
	:param min_level: 切片最小层级
	:param max_level: 切片最小层级
	:param coord: 投影坐标系
	:param out_path: lerc文件路径
	:return: None
	'''
	if coord == 4490:
		cmd = "python /home/gago_developers/jilin_tools/multi_tiff2lerc_2000.py %s %02d %02d %s" % (input_path, min_level, max_level, out_path)  # 1km level 7 to 8
		os.system(cmd)
	elif coord == 4326:
		cmd = "python /home/gago_developers/jilin_tools/multi_tiff2lerc_new.py %s %02d %02d %s" % (input_path, min_level, max_level, out_path)  # 1km level 7 to 8
		os.system(cmd)


def tiff_mask(intiff:str, mask_tiff:str, outtiff:str, nodata:int) -> None:
	'''
	栅格作物掩膜
	前提气象栅格和作物栅格数据，四至和分辨率均相同，完全对齐
	:param intiff: 未掩膜文件
	:param mask_tiff: 掩膜文件
	:param outtiff: 已掩膜文件
	:return: None
	'''
	if os.path.exists(outtiff):
		os.remove(outtiff)
	cmd = 'gdal_calc.py -A %s -B %s --outfile=%s --calc="A*B" --NoDataValue=%s'%(intiff, mask_tiff, outtiff, str(nodata))
	os.system(cmd)


def get_critical_para(critical_date: list, critical_var: list, date: datetime.date) -> int:
    '''
    根据生育期时间点，返回气象要素阈值
    :param critical_date: 阈值起始时间的list
    :param critical_var:  阈值的list
    :param date: 要计算的那一天日期，datetime.date
    :return: 对应物候期阈值
    '''
    year = date.year
    first = datetime.date(year, int(critical_date[0][:2]), int(critical_date[0][2:]))
    last = datetime.date(year, int(critical_date[-1][:2]), int(critical_date[-1][2:]))
    if date < first:
        return critical_var[0]
    elif date > last:
        return critical_var[-1]
    else:
        for i in range(len(critical_date) - 1):
            if int(critical_date[i]) > int(critical_date[i + 1]):
                bottom = datetime.date(year, int(critical_date[i][:2]), int(critical_date[i][2:]))
                top = datetime.date(year + 1, int(critical_date[i + 1][:2]), int(critical_date[i + 1][2:]))
                if (date >= bottom) and (date <= top):
                    return critical_var[i]
            else:
                bottom = datetime.date(year, int(critical_date[i][:2]), int(critical_date[i][2:]))
                top = datetime.date(year, int(critical_date[i + 1][:2]), int(critical_date[i + 1][2:]))
                if (date >= bottom) and (date <= top):
                    print('critical_var: ', critical_var[i])
                    return critical_var[i]


def t2m_hourly(tmaxlast:np.array, tmax:np.array, tmin:np.array, tminnext:np.array, hour:int) -> np.array:
	"""
	彭博士的温度插值法
	:param tmaxlast: 前一天的最高温
	:param tmax: 当天最高温
	:param tmin: 当天最低温
	:param tminnext: 下一天最低温
	:param hour: 当天的小时0~23
	:return: 一天内各小时平均温度
	"""
	ny, nx = np.array(tmax).shape
	# t2m_hourly = np.zeros((ny, nx))
	omega = 3.1416 / 12
	Gamma = 0.44 - 0.46 * np.sin(omega * hour + 0.9) + 0.11 * np.sin(2 * omega * hour + 0.9)
	if hour < 5:
		t2m_hourly = tmaxlast * Gamma + tmin * (1 - Gamma)
	elif 5 <= hour <= 14:
		t2m_hourly = tmax * Gamma + tmin * (1 - Gamma)
	else:
		t2m_hourly = tmax * Gamma + tminnext * (1 - Gamma)

	return t2m_hourly