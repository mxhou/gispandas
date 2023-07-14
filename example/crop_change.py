# -*- encoding: utf-8 -*-
'''
@File    :   crop_change.py
@Time    :   2023/07/14 13:42:59
@Author  :   HMX
@Version :   1.0
@Contact :   kzdhb8023@163.com
'''

# here put the import lib
import time
import gispandas as gp


if __name__ == '__main__':
    t1 = time.time()
    lasttif = r'E:\Project\潍坊项目v2\数据统计v2\种植结构+面积+产量\data\wheat\wheat_2022.tif'
    nowtif = r'E:\Project\潍坊项目v2\数据统计v2\种植结构+面积+产量\data\wheat\wheat_2023.tif'
    outtif = r'E:\Project\潍坊项目v2\数据统计v2\种植结构+面积+产量\data\wheat\wheat_change_2023_test.tif'
    outjson = r'E:\Project\潍坊项目v2\数据统计v2\种植结构+面积+产量\data\wheat\wheat_change_2023.json'
    shpfp = r'E:\Project\潍坊项目v2\客户矢量v5\all\wf_all2000_info.geojson'
    gridcode = 107
    gp.cropchg(lasttif,nowtif,outtif,outjson,shpfp,gridcode,nodata = 0,resolution=10,year=time.strftime('%Y'),code = 'code',name = 'name')
    print(time.time()-t1)
