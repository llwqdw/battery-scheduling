'''
生成站点距离表 站点电池容积列表 货车容积
'''

import pandas as pd
import numpy as np
import datetime
import time
import json
import math
from geopy.distance import geodesic
from sqlalchemy import create_engine

def ceDiXian_distance(lat_origin, lng_origin, lat_destination, lng_destination):
    distance = geodesic((float(lat_origin),float(lng_origin)), (float(lat_destination),float(lng_destination))).kilometers
    return distance

df2 = pd.read_excel("dataExecute/data/oriData/xl_cgstationnetworkInfo_cd_20241009_formal.xlsx")
for i in range(df2.shape[0]):
    df2.loc[i,'code'] = str(df2.loc[i,'code']) 
cgCodeL = [a for a in list(df2["code"])]

'''
处理距离表
'''

depotGps = [104.076725,30.609007] # 设置仓库坐标

distT = [[0 for j in range(len(cgCodeL)+1)] for i in range(len(cgCodeL)+1)] # 距离表
gpsL = [depotGps]
for i in range(len(cgCodeL)):
    gpsL.append([df2.loc[i]['lng'],df2.loc[i]['lat']])

for i in range(len(cgCodeL)+1):
    for j in range(len(cgCodeL)+1):
        if i!=j:
            distance = ceDiXian_distance(gpsL[i][1],gpsL[i][0],gpsL[j][1],gpsL[j][0])
            distT[i][j] = distance

'''
处理货车容积
'''
truckCapacity = 300 # 货车容积

np.savez('dataExecute/data/testData/staBasicData.npz',distT=distT,truckCapacity=truckCapacity)