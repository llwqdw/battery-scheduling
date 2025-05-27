import pandas as pd
import numpy as np
import datetime
import json
import holidays
import time
from decimal import Decimal, ROUND_HALF_UP

# '''
# 额外处理station_battery_cd_data_20241024表
# '''
# f1 = open('data/station_battery_cd_data_20241024.csv','r')
# f2 = open('data/station_battery_cd_data_20241024_simple.csv','w')
# i = 0
# for line in f1.readlines():
#     if i==0:
#         f2.write(line)
#         i += 1
#         continue
#     if line[-9:-7] == '00':
#         f2.write(line)
# f2.close()

'''
处理场景数据 20240923-20240929
生成站点特征数据文件 站点未来时段需求文件 站点当前电池数文件 站点电池充电速度文件 站点未来一天需电池数文件
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
end_slot = "2024-09-30 00:00:00"
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

# '''
# 处理站点特征数据文件 站点未来时段需求文件
# '''
# t1 = time.time()

# # 提取气象特征: 天气
# weaCodeD = {'晴朗':0,'雨天':1,'雪天':2}
# temperCodeD = {'<15':0,'15-30':1,'>=30':2}
# windSCodeD = {'<=3(微风)':0,'>3(大风)':1}
# df2 = pd.read_excel('dataExecute/data/normalData/wea_cd_20221201_20241101.xlsx')
# meteoDict = dict()
# for i in range(df2.shape[0]):
#     dayStr = df2.loc[i]['日期'][:10].replace('-','')
#     weaStr = df2.loc[i]['天气']
#     wea = weaStr
#     if '~' in weaStr:
#         wea = weaStr.split('~')[0]
#     elif '转' in weaStr:
#         wea = weaStr.split('转')[0]
#     if '雨' in wea:
#         weaCode = 1
#     elif '雪' in wea:
#         weaCode = 2
#     else:
#         weaCode = 0
#     temperMax = int(df2.loc[i]['最高温度'].split('℃')[0])
#     temperMin = int(df2.loc[i]['最低温度'].split('℃')[0])
#     temper = round((temperMax+temperMin)/2)
#     if temper<15:
#         temperCode = 0
#     elif temper>=15 and temper<30:
#         temperCode = 1
#     else:
#         temperCode = 2
#     if '级' not in df2.loc[i]['风向']:
#         if '微' in df2.loc[i]['风向']:
#             windSCode = 0
#         else:
#             windSCode = 1
#     else:
#         windS = int(df2.loc[i]['风向'][-2])
#         if windS<=3:
#             windSCode = 0
#         else:
#             windSCode = 1
#     meteoDict[dayStr] = [weaCode,temperCode,windSCode]

# dayFeaDict = dict() # 站点特征数据文件 {天: [站点索引[时段索引[特征]]]}
# dayTruthDemandDict = dict() # 站点未来时段需求文件 {天: [站点索引[时段索引[真值]]]}
# # 提取时间特征: 一周中的天数、一天的时段、是否节假日
# for vDay in validDayL:
#     list1 = [];list1_a = []
#     vDayI = dayIndexDict[vDay]
#     i = vDayI
#     dayStr = vDay
#     date=datetime.datetime.strptime(dayStr, "%Y%m%d")
#     dateUnix = time.mktime(date.timetuple())
#     dayNo = date.weekday()
#     if dayNo in [5,6]:
#         isWeekend = 1
#     else:
#         isWeekend = 0
#     if date in holidays.China():
#         isHoliday = 1
#     else:
#         isHoliday = 0

#     for j in range(len(demandSSL[0])): # 站点索引
#         list2 = [];list2_a = []
#         for k in range(len(demandSSL[0][0])): # 时段索引
#             preL = [demandSSL[i-p][j][k] for p in range(1,8)]
#             truth = demandSSL[i][j][k]
#             # [站点索引,一周天索引,时段索引,是否节假日,前7天需求,天气,温度,风速]
#             list3 = [j,dayNo,k,isHoliday]+preL+[meteoDict[dayStr][0],
#                      meteoDict[dayStr][1],meteoDict[dayStr][2]]
#             list3_a = truth
#             list2.append(list3);list2_a.append(list3_a)
#         list1.append(list2);list1_a.append(list2_a)
#     dayFeaDict[vDay] = list1;dayTruthDemandDict[vDay] = list1_a

# np.save('dataExecute/data/testData/demadPredInputDict.npy',dayFeaDict)
# np.save('dataExecute/data/testData/dayTruthDemandDict.npy',dayTruthDemandDict)
# t2 = time.time()
# print(1,t2-t1,'s')

'''
处理站点当前电池数文件 站点电池充电速度文件
'''
t1 = time.time()
df2 = pd.read_csv("dataExecute/data/testData/station_battery_cd_data_20241024_simple.csv",delimiter=";;",engine="python")
staChargeRateL = np.load('dataExecute/data/testData/staChargeRateL.npy')

df2["time_unix"] = [time.mktime(datetime.datetime.strptime(a, '%Y-%m-%d %H:%M:%S').timetuple()) for a in list(df2["created"])]
dayStaBatteryDict = dict() # 站点电池数数据文件 {天: [站点索引[电池个数,[电池电量],站点容积,站点电池充电速度]]}
for i in range(len(validDayL)):
    vDay = validDayL[i]
    vDayI = dayIndexDict[vDay]
    dayU = daySlotUnixList[i]
    list1 = []
    for j in range(len(cgCodeL)): # 站点电池状态初始化
        list1.append([0,[],0,0])
    dayDf = df2[(df2["time_unix"]>=dayU) & (df2["time_unix"]<dayU+10*60)] # 10min
    for j in range(dayDf.shape[0]):
        cgCode = str(dayDf.iloc[j][1])
        if cgCode in cgCodeL and list1[staIndexDict[cgCode]][2]==0:
            capacity = df1.loc[staIndexDict[cgCode],'cell_num']
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
            list1[staIndexDict[cgCode]][1] = batteryL
            list1[staIndexDict[cgCode]][2] = capacity
            list1[staIndexDict[cgCode]][3] = staChargeRateL[staIndexDict[cgCode]] # 默认每分钟充电0.3%
    dayStaBatteryDict[vDay] = list1
np.save('dataExecute/data/testData/stationBatteryStateDict.npy',dayStaBatteryDict)

t2 = time.time()
print(2,t2-t1,'s')

# '''
# 处理站点未来一天需电池数真值文件
# '''
# t1 = time.time()
# # 读取站点每天需电池数数据
# batteryNDict = json.load(open('dataExecute/data/normalData/satisfiedBattertyNRsoc_cd_20221201_20241009.json','r'))
# dayTruthbatteryNDict = dict() # 站点每天需电池数文件 {天: [站点索引[真值]]}
# for vDay in validDayL:
#     list1 = []
#     vDayI = dayIndexDict[vDay]
#     for j in range(len(demandSSL[0])): # 站点索引
#         dayAllDemand = np.sum(np.array(demandSSL[vDayI][j]))
#         batteryNum = batteryNDict[vDay][j]
#         satisfiedBatteryN = batteryNum
#         list1.append(satisfiedBatteryN)
#     dayTruthbatteryNDict[vDay] = list1
# np.save('dataExecute/data/testData/dayTruthbatteryNDict.npy',dayTruthbatteryNDict)
# t2 = time.time()
# print(3,t2-t1,'s')