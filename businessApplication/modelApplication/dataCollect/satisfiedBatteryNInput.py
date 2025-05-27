import pandas as pd
import numpy as np
import datetime
import json
import holidays
import time
from decimal import Decimal, ROUND_HALF_UP

'''
生成站点需电池数预测模型输入数据
'''

battertyNData = json.load(open('dataExecute/data/normalData/satisfiedBattertyNRsoc_cd_20221201_20241009.json','r'))
battertyNDayL = list(battertyNData.keys()) # 存储天列表
battertyNSSL = list(battertyNData.values()) # 存储天站点时段索引需求数列表

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
for index,day in enumerate(battertyNDayL):
    dayIndexDict[day] = index

'''
处理站点特征数据文件 站点未来时段需求文件
'''

# 提取气象特征: 天气
weaCodeD = {'晴朗':0,'雨天':1,'雪天':2}
temperCodeD = {'<15':0,'15-30':1,'>=30':2}
windSCodeD = {'<=3(微风)':0,'>3(大风)':1}
df2 = pd.read_excel('dataExecute/data/normalData/wea_cd_20221201_20241101.xlsx')
meteoDict = dict()
for i in range(df2.shape[0]):
    dayStr = df2.loc[i]['日期'][:10].replace('-','')
    weaStr = df2.loc[i]['天气']
    wea = weaStr
    if '~' in weaStr:
        wea = weaStr.split('~')[0]
    elif '转' in weaStr:
        wea = weaStr.split('转')[0]
    if '雨' in wea:
        weaCode = 1
    elif '雪' in wea:
        weaCode = 2
    else:
        weaCode = 0
    temperMax = int(df2.loc[i]['最高温度'].split('℃')[0])
    temperMin = int(df2.loc[i]['最低温度'].split('℃')[0])
    temper = round((temperMax+temperMin)/2)
    if temper<15:
        temperCode = 0
    elif temper>=15 and temper<30:
        temperCode = 1
    else:
        temperCode = 2
    if '级' not in df2.loc[i]['风向']:
        if '微' in df2.loc[i]['风向']:
            windSCode = 0
        else:
            windSCode = 1
    else:
        windS = int(df2.loc[i]['风向'][-2])
        if windS<=3:
            windSCode = 0
        else:
            windSCode = 1
    meteoDict[dayStr] = [weaCode,temperCode,windSCode]

dayFeaDict = dict() # 站点特征数据文件 {天: [站点索引[特征]]}
# 提取时间特征: 一周中的天数、一天的时段、是否节假日
for vDay in validDayL:
    list1 = []
    vDayI = dayIndexDict[vDay]
    i = vDayI
    dayStr = vDay
    date=datetime.datetime.strptime(dayStr, "%Y%m%d")
    dateUnix = time.mktime(date.timetuple())
    dayNo = date.weekday()
    if dayNo in [5,6]:
        isWeekend = 1
    else:
        isWeekend = 0
    if date in holidays.China():
        isHoliday = 1
    else:
        isHoliday = 0

    for j in range(len(battertyNSSL[0])): # 站点索引
        # 提取历史使用特征: 历史7天同一时段的用户需求量
        preL = [battertyNSSL[i-p][j] for p in range(1,8)]
        truth = battertyNSSL[i][j]
        # [站点索引,一周天索引,时段索引,是否节假日,前7天需电池数,天气,温度,风速,未来一天需电池数]
        list2 = [j,dayNo,0,isHoliday]+preL+[meteoDict[dayStr][0],
                    meteoDict[dayStr][1],meteoDict[dayStr][2]]
        list1.append(list2)
    dayFeaDict[vDay] = list1

np.save('dataExecute/data/applicationData/satisfiedBatteryNInputDict.npy',dayFeaDict)