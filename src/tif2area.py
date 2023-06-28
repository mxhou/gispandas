# -*- encoding: utf-8 -*-
'''
@File    :   tif2area.py
@Time    :   2023/06/19 10:06:19
@Author  :   HMX
@Version :   1.0
@Contact :   kzdhb8023@163.com
'''

# here put the import lib
import os
import sys
import pandas as pd
import time
sys.path.append(r'E:\Project\code\分类统计\count_tif_area\code')
from tif2json_v3 import *

if __name__=='__main__':
    t1 = time.time()
    # tiffp = r'F:\Project2\潍坊项目v2\out\wheat23_v7.tif'
    # tiffp = r'E:\Project\潍坊项目v2\数据统计v2\wheat\wheat_2022.tif'
    # tiffp = r'F:\Project2\潍坊项目v2\out2\wheat23_v6.tif'
    tiffp = r'F:\Project2\潍坊项目v2\final\wheat2023.tif'
    # tiffp = r'F:\Project2\潍坊项目v2\out2\wheat_v6_v2_out_v4.tif'
    # tiffp = r'F:\Project2\潍坊项目v2\out2\wheat23_v7_v2.tif'
    shpfp = r'E:\Project\潍坊项目v2\客户矢量v5\all\wf_all2000_info.geojson'
    tempfp = r'E:\Project\潍坊项目v2\数据统计v2\分类数据v3\temp'
    class_dic = {'wheat': 107}
    print(class_dic)

    outjson = os.path.join(r'E:\Project\潍坊项目v2\数据统计v2\分类数据v3\data',os.path.basename(tiffp)[:-4]+'.json')
    main(tiffp,shpfp,tempfp,class_dic,outjson)
    # print(pd.read_json(outjson))
    df = pd.read_json(outjson)
    # df= df[df['name']=='潍坊市']
    # df['rate'] = df['area']/df['area'].sum()
    # df['rate'] = df['rate'].apply(lambda x: '{:.2%}'.format(x))
    df['area'] = df['area']
    # df['area_ha'] = df['area']/15
    print(df.head(16))

    fn22 = r'E:\Project\潍坊项目v2\数据统计v2\分类数据v3\data\wheat_2022.json'
    # fn23 = r'E:\Project\潍坊项目v2\数据统计v2\分类数据v3\data\wheat23_v7.json'
    # fn23 = r'E:\Project\潍坊项目v2\数据统计v2\分类数据v3\data\wheat23_v7_v2.json'
    # fn23 = r'E:\Project\潍坊项目v2\数据统计v2\分类数据v3\data\wheat23_v2.json'
    # fn23 = r'E:\Project\潍坊项目v2\数据统计v2\分类数据v3\data\wheat23_v3.json'
    # print(os.path.basename(fn23))
    df22 = pd.read_json(fn22)
    # df23 = pd.read_json(fn23)
    # print(df22,df23)
    res = pd.merge(df22,df,on = ['code', 'name', 'type','year'],how = 'inner')
    res['rate'] = res['area_y']/res['area_x']-1
    res['rate'] = res['rate'].apply(lambda x: '{0:.2f}%'.format(x*100))
    # res['area_y_ha']
    print(res.head(16))
    print('共计用时{:.2f}s'.format(time.time()-t1))
    res = res.rename(columns={'area_x':'area2022', 'area_y':'area2023'})
    res.to_excel(r'E:\Project\潍坊项目v2\数据统计v2\分类数据v3\data\wheat2023.xlsx',index=False)