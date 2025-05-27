import pandas as pd
import numpy as np
import datetime
import json
import time

'''
获取当前时刻站点电池个数
'''

# 读取用户需求数据
demandData = json.load(open('dataExecute/data/normalData/demand_data_cd_20221201_20241009_1day.json','r'))
demandDayL = list(demandData.keys()) # 存储天列表
demandSSL = list(demandData.values()) # 存储天站点时段索引需求数列表
print(len(demandData))

# 读取站点表
df1 = pd.read_excel("dataExecute/data/oriData/xl_cgstationnetworkInfo_cd_20241009_formal.xlsx")
for i in range(df1.shape[0]):
    df1.loc[i,'code'] = str(df1.loc[i,'code']) 
cgCodeL = [a for a in list(df1["code"])]

validDayL = [] # 目标天数列表
start_slot = "2024-09-23 00:00:00"
d = datetime.datetime.strptime(start_slot, '%Y-%m-%d %H:%M:%S')
start_slot_unix = time.mktime(d.timetuple())
end_slot = "2024-09-24 00:00:00"
d = datetime.datetime.strptime(end_slot, '%Y-%m-%d %H:%M:%S')
end_slot_unix = time.mktime(d.timetuple())
day_unix = 24*3600 # 1d
for i in range(int((end_slot_unix-start_slot_unix)/day_unix)):
    dayU = start_slot_unix+i*day_unix
    dayStan = str(datetime.datetime.fromtimestamp(dayU))
    dayStr = dayStan.replace("-","")[0:8]
    validDayL.append(dayStr)
# print(validDayL)
daySlotUnixList = []
for i in range(int((end_slot_unix-start_slot_unix)/day_unix)):
    dayU = start_slot_unix+i*day_unix
    daySlotUnixList.append(dayU)

dayIndexDict = dict() # 建立天索引字典
for index,day in enumerate(demandDayL):
    dayIndexDict[day] = index

staIndexDict = dict() # 建立站点索引字典
for index,sta in enumerate(cgCodeL):
    staIndexDict[sta] = index

t1 = time.time()
df2 = pd.read_csv("dataExecute/data/testData/station_battery_cd_data_20241024_simple.csv",delimiter=";;",engine="python")

df2["time_unix"] = [time.mktime(datetime.datetime.strptime(a, '%Y-%m-%d %H:%M:%S').timetuple()) for a in list(df2["created"])]
dayStaBatteryDict = dict() # 站点电池数数据文件 {天: [站点索引[电池个数,[电池电量],站点容积,站点电池充电速度]]}
for i in range(len(validDayL)):
    vDay = validDayL[i]
    vDayI = dayIndexDict[vDay]
    dayU = daySlotUnixList[i]
    list1 = []
    for j in range(len(cgCodeL)): # 站点电池状态初始化
        list1.append([0,0])
    dayDf = df2[(df2["time_unix"]>=dayU) & (df2["time_unix"]<dayU+10*60)] # 10min
    for j in range(dayDf.shape[0]):
        cgCode = str(dayDf.iloc[j][1])
        if cgCode in cgCodeL and list1[staIndexDict[cgCode]][1]==0:
            capacity = 0
            tmp = cgCode
            k = j
            # 统计站点容积
            while True:
                door_id = dayDf.iloc[k,2]
                capacity = max(capacity,door_id)
                k += 1
                tmp = str(dayDf.iloc[k][1])
                if tmp!=cgCode or k>=dayDf.shape[0]:
                    break
            batteryL = []
            tmp = cgCode
            k = j
            acc = 0
            # 统计站点当前电池数量
            while True:
                device_id = str(dayDf.iloc[k,4])
                if not(device_id=='0.0' or device_id=='null' or device_id=='nan'):
                    soc = dayDf.iloc[k,5]
                    batteryL.append(soc)
                k += 1
                acc += 1
                tmp = str(dayDf.iloc[k][1])
                if tmp!=cgCode or k>=dayDf.shape[0] or acc>=capacity:
                    break
            list1[staIndexDict[cgCode]][0] = len(batteryL)
            list1[staIndexDict[cgCode]][1] = capacity
    dayStaBatteryDict[vDay] = list1
np.save('dataExecute/data/applicationData/stationBatteryStateDict.npy',dayStaBatteryDict)