# -*- encoding: utf-8 -*-
'''
@File    :   caltifarae.py
@Time    :   2023/06/28 09:55:35
@Author  :   HMX
@Version :   1.0
@Contact :   kzdhb8023@163.com
'''

# here put the import lib
import sys
sys.path.append('E:\Project\gispandas\src')
import  gispandas.gispandas as gp
import pandas as pd
import numpy as np
import geopandas as gpd
import time

if __name__ == '__main__':
    t1 = time.time()
    intif = r'E:\Project\潍坊项目v2\估产\估产v2\outdata\out\wheat_2023.tif'
    inshp = r'E:\Project\潍坊项目v2\客户矢量v5\all\wf_all2000_info.geojson'
    class_dic = {"wheat": 107}
    outjson = r'E:\Project\gispandas\example\wheat23.json'
    gp.tif2area(intif,inshp,class_dic,outjson,year = 2022)
    t2 = time.time()
    print('共计用时{:.2f}s'.format(t2 -t1))
    df = pd.read_json(outjson)
    print(df)