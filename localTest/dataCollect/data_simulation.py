'''
处理实验测试数据
包括每个时段的用户换电情况
'''

import pandas as pd
import numpy as np
import datetime
import time
import json
import math

'''
用户换入电池情况统计
'''

t1 = time.time()

df1 = pd.read_csv("dataExecute/data/testData/battery_change_data_20240901_20241001.csv",delimiter=";;",engine="python")
df1["time_unix"] = [time.mktime(datetime.datetime.strptime(a, '%Y-%m-%d %H:%M:%S').timetuple()) 
                    for a in list(df1["created"])]
df2 = pd.read_excel("dataExecute/data/oriData/xl_cgstationnetworkInfo_cd_20241009_formal.xlsx")
for i in range(df2.shape[0]):
    df2.loc[i,'code'] = str(df2.loc[i,'code']) 
cgCodeL = [a for a in list(df2["code"])]

# 存储每个站点的pandas列
stationDfDict = dict()
for cgCode in cgCodeL:
    staDf = df1[(df1["cg_code"]==cgCode)]
    stationDfDict[cgCode] = staDf

start_slot = "2024-09-23 00:00:00"
d = datetime.datetime.strptime(start_slot, '%Y-%m-%d %H:%M:%S')
start_slot_unix = time.mktime(d.timetuple())
end_slot = "2024-09-30 00:00:00"
d = datetime.datetime.strptime(end_slot, '%Y-%m-%d %H:%M:%S')
end_slot_unix = time.mktime(d.timetuple())
day_unix = 24*3600 # 1d
slot_unix = 5*60 # 单位时段长度 1h 可定为10min 5min
dayN = math.ceil((end_slot_unix-start_slot_unix)/day_unix)

daySlotUnixList = [] # 存储一天的unix
for i in range(int((end_slot_unix-start_slot_unix)/day_unix)):
    dayU = start_slot_unix+i*day_unix
    daySlotUnixList.append(dayU)
daySlotUnixDict = dict() # 存储一天各时段的unix
for i in range(int((end_slot_unix-start_slot_unix)/day_unix)):
    dayU = start_slot_unix+i*day_unix
    dayStan = str(datetime.datetime.fromtimestamp(dayU))
    dayStr = dayStan.replace("-","")[0:8]
    daySlotUnixDict[dayStr] = [dayU+j*slot_unix for j in range(int(day_unix/slot_unix))]

dayCgSlotDict = dict() # dict{dayStr:list_station[list_slot[换入电量1,换入电量2]]} 每日标准化文件

# 生成标准化每日文件
for dayStr in daySlotUnixDict.keys():
    list1 = []
    for cgCode in cgCodeL:
        staDf = stationDfDict[cgCode]
        list2 = []
        dayDemandNum = 0
        for unix1 in daySlotUnixDict[dayStr]:
            list3 = []
            df3 = staDf[(staDf["time_unix"]>=unix1)&(staDf["time_unix"]<unix1+slot_unix)]
            for rowI in list(df3.index):
                rsoc = str(df3.loc[rowI,'o_rsoc'])
                if rsoc=='null' or rsoc=='nan':
                    rsoc = 55 # 若换入电量缺失则默认用户换入电量为55
                list3.append(float(rsoc))
            list2.append(list3)
        list1.append(list2)
    dayCgSlotDict[dayStr] = list1
    print(dayStr)

wf1 = open("dataExecute/data/testData/data_simulation.json","w")
vJson = json.dumps(dayCgSlotDict)
wf1.write(vJson)
wf1.close()

t2 = time.time()
print(1, t2-t1,'s')