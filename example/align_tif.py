# -*- encoding: utf-8 -*-
'''
@File    :   align_tif.py
@Time    :   2023/07/13 11:19:48
@Author  :   HMX
@Version :   1.0
@Contact :   kzdhb8023@163.com
'''

# here put the import lib
import gispandas as gp

fn22 = r'E:\Project\潍坊项目v2\数据统计v2\种植结构+面积+产量\data\wheat\wheat_2022.tif'
fn23 = r'E:\Project\潍坊项目v2\数据统计v2\种植结构+面积+产量\data\wheat\wheat_2023.tif'

gp.aligntif(fn23,fn23.replace('.tif','_align_mxgdal.tif'),fn22)
print('ok')
