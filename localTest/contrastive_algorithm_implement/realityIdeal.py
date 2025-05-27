import sys
import os
sys.path.append(os.path.abspath(os.path.join(sys.path[0], '../..')))
sys.path.append(os.path.abspath(os.path.join(sys.path[0], '..')))
from algothrim.scenario_simulationIdeal import scenario_simulationIdeal
import json
import time
import numpy as np
import pandas as pd

t1 = time.time()

algName = 'realityIdeal'
dayFeaDict = np.load('dataExecute/data/testData/demadPredInputDict.npy', allow_pickle=True).item()
dayStaBatteryDict = np.load('dataExecute/data/testData/stationBatteryStateDict.npy', allow_pickle=True).item()
# 存储仿真实验数据
simulationDayData = json.load(open('dataExecute/data/testData/data_simulation.json','r'))

testDayL = list(dayFeaDict.keys())

evalDict = dict()
evalIndexList = ['事件','用户需求满足百分比','用户平均换出电量_只换出','用户平均换出电量_全部需求']
for evalIndex in evalIndexList:
    evalDict[evalIndex] = []

allDN = 0
notSatN = 0

for i in range(len(testDayL)):
    testDay = testDayL[i]
    evalDict[evalIndexList[0]].append(testDay)
    print(f'process {i} {testDay}')

    staBatteryInfo = dayStaBatteryDict[testDay]
    processDict = dict()
    routeTrue = []
    histBestBalanceNL = []
    routeSimu = routeTrue[1:]
    balanceNLSimu = histBestBalanceNL[1:]
    # 进行场景模拟 计算用户需求满足百分比
    simulationData = simulationDayData[testDay]
    a,b = scenario_simulationIdeal(simulationData,staBatteryInfo,routeSimu,balanceNLSimu,processDict,
                        evalDict,evalIndexList[1],evalIndexList[2],evalIndexList[3])
    allDN += a
    notSatN += b
    # break

for i in range(len(evalIndexList)):
    if i==0:
        value = 'aver'
    elif i==1:
        arr1 = np.array(evalDict[evalIndexList[i]])
        avr = np.mean(arr1,axis=0)
        value = [avr,notSatN,allDN]
    else:
        arr1 = np.array(evalDict[evalIndexList[i]])
        avr = np.mean(arr1,axis=0)
        value = avr
    evalDict[evalIndexList[i]].append(value)

# # evalDict自动填补
# evalLen = len(evalDict[evalIndexList[0]])
# for evalIndex in evalIndexList:
#     for j in range(len(evalDict[evalIndex]),evalLen):
#         evalDict[evalIndex].append(None)
# print(evalDict)

df1 = pd.DataFrame(evalDict)
df1.to_excel(f'localTest/result/simulation/evaluation/{algName}_evaluation.xlsx',index=False)

t2 = time.time()
print(f"time cost: {t2-t1} s")