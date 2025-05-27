'''
主程序
'''
import sys
import os
sys.path.append(os.path.abspath(os.path.join(sys.path[0], '..')))
from demandPred import demandPred
from rebalancingRange import rebalancingRange
import json
import time
import numpy as np
import pandas as pd
import joblib
import copy
import datetime

t1 = time.time()

demandData = json.load(open('dataExecute/data/normalData/demand_data_cd_20221201_20241009_1day.json','r')) # 需求数据
demandSSL = list(demandData.values())
staN = len(demandSSL[0]) # 站点个数
slotN = len(demandSSL[0][0]) # 时段个数

# 读取站点表
df1 = pd.read_excel("dataExecute/data/oriData/xl_cgstationnetworkInfo_cd_20241009_formal.xlsx")

# 存储0点站点需求预测特征数据 站点需求真值数据 站点电池状态数据(电池个数,[电池电量],站点容积,站点电池充电速度)
dayFeaDict = np.load('dataExecute/data/applicationData/demadPredInputDict.npy', allow_pickle=True).item()
dayBatteryNFeaDict = np.load('dataExecute/data/applicationData/satisfiedBatteryNInputDict.npy', allow_pickle=True).item()
dayStaBatteryDict = np.load('dataExecute/data/applicationData/stationBatteryStateDict.npy', allow_pickle=True).item()
demandPreModel = joblib.load('businessApplication/model/demandPredModel.joblib')
batterNPreModel = joblib.load('businessApplication/model/satisfiedBattertyNPredModel.joblib')

testDayL = list(dayFeaDict.keys())
testDay = testDayL[0]

staFeaL = np.array(dayFeaDict[testDay])
staBatteryNFeaL = np.array(dayBatteryNFeaDict[testDay])
staBatteryInfo = dayStaBatteryDict[testDay]

################################
########### 需求预测 ############
################################
'''
未来各时段站点用户需求预测
'''
demand_pred = demandPred(staN,slotN,staFeaL,demandPreModel)

###################################
########### 站点状态评估 ###########
###################################
'''
站点电池调度数量范围计算
'''
# LR 左闭右闭
predL,LR = rebalancingRange(demand_pred,staBatteryInfo,batterNPreModel,staBatteryNFeaL)
df2 = copy.deepcopy(df1)
df2['requiredBattertNum'] = predL
df2['rebalancingNum'] = [a[1] for a in LR]
df2['predictTime'] = [datetime.datetime.now() for a in LR]

df2.to_excel('dataExecute/data/applicationData/stationRebalancingResult.xlsx',index=False)

t2 = time.time()
print('结果已存储至dataExecute/data/applicationData/stationRebalancingResult.xlsx')
print(f"时间耗费: {t2-t1} s")