'''
主程序
'''
import sys
import os
sys.path.append(os.path.abspath(os.path.join(sys.path[0], '..')))
from algothrim.demandPred import demandPred
from algothrim.rebalancingRange_method2_multiFea import rebalancingRange_method2_multiFea
from algothrim.scenario_simulation import scenario_simulation
from algothrim.routePlanning_parallel import SA_parallel
from algothrim.exceptionBatteryNum import exceptionBatteryNum
from algothrim.confirmVisit import confirmVisit
import json
import time
import numpy as np
import pandas as pd
import joblib

t1 = time.time()

algName = 'ours_multiFea_sumDemand'
demandData = json.load(open('dataExecute/data/normalData/demand_data_cd_20221201_20241009_1day.json','r')) # 需求数据
demandSSL = list(demandData.values())
staN = len(demandSSL[0]) # 站点个数
slotN = len(demandSSL[0][0]) # 时段个数

# 存储站点基本信息 包括站点距离表 货车容积
staBasicData = np.load('dataExecute/data/testData/staBasicData.npz')
# 存储0点站点需求预测特征数据 站点需求真值数据 站点电池状态数据(电池个数,[电池电量],站点容积,站点电池充电速度)
dayFeaDict = np.load('dataExecute/data/testData/demadPredInputDict.npy', allow_pickle=True).item()
dayBatteryNFeaDict = np.load('dataExecute/data/testData/satisfiedBatteryNInputDict.npy', allow_pickle=True).item()
dayTruthDemandDict = np.load('dataExecute/data/testData/dayTruthDemandDict.npy', allow_pickle=True).item()
dayStaBatteryDict = np.load('dataExecute/data/testData/stationBatteryStateDict.npy', allow_pickle=True).item()
# 存储站点每天需电池数真值数据
dayTruthbatteryNDict = np.load('dataExecute/data/testData/dayTruthbatteryNDict.npy', allow_pickle=True).item()
# 存储仿真实验数据
simulationDayData = json.load(open('dataExecute/data/testData/data_simulation.json','r'))
demandPreModel = joblib.load('localTest/model/demandPredModel.joblib')
batterNPreModel = joblib.load('localTest/model/satisfiedBattertyNPredModel.joblib')

testDayL = list(dayFeaDict.keys())
disT = staBasicData['distT'] # 站点距离表
print(np.array(disT).shape)
C = staBasicData['truckCapacity'] # 货车电池容积
r1 = 10;r2 = 1 # 统一度量(与温度数值相当) 货车行驶100m相当于换电站操作1块电池

evalDict = dict()
evalIndexList = ['事件','用户需求预测(RMSE,MAE)','站点可满足电池数预测(RMSE,MAE)','调度成本(总距离,总调度电池数)',
                 '用户需求满足百分比','用户平均换出电量_只换出','用户平均换出电量_全部需求']
for evalIndex in evalIndexList:
    evalDict[evalIndex] = []
# processStaL = ['demandPre','demandTruth','satisfiedBatteryNInput','satisfiedBatteryNInputTruth',
#                'satisfiedBatteryNPred','satisfiedBatteryNTruth','isValid','staBatteryN','LR_1',
#                'requireNDecrease','LR_2','isVisit']
# processDayL = ['batteryAvailN,requireN,decreaseN','visitAvailN','distSum','balanceSum','balanceAbsSum',
#                'histBestDist','routeTrue','histBestBalanceNL','demandNSimu','notSatisfiedDemandNSimu']
processStaL = ['demandPre','demandTruth','satisfiedBatteryNInput','satisfiedBatteryNInputTruth',
               'satisfiedBatteryNPred','satisfiedBatteryNTruth','isValid','staBatteryN','LR_1',
               'requireNDecrease','LR_2','isVisit']
processDayL = ['day','batteryAvailN,requireN,decreaseN,newAvailN,newRequireN','visitAvailN,visitStaN','distSum','balanceSum',
               'balanceAbsSum','histBestDist','routeTrue','histBestBalanceNL','demandNSimu',
               'notSatisfiedDemandNSimu']
processAllDayDict = dict()
for processIndex in processDayL:
    processAllDayDict[processIndex] = []

allDN = 0
notSatN = 0

for i in range(len(testDayL)):
    # if i>3:
    #     continue
    testDay = testDayL[i]

    processAllDayDict[processDayL[0]].append(testDay)
    evalDict[evalIndexList[0]].append(testDay)
    print(f'process {i} {testDay}')

    staFeaL = np.array(dayFeaDict[testDay])
    staBatteryNFeaL = np.array(dayBatteryNFeaDict[testDay])
    staTruthDemandL = np.array(dayTruthDemandDict[testDay])
    staBatteryInfo = dayStaBatteryDict[testDay]
    staTruthbatteryNL = np.array(dayTruthbatteryNDict[testDay])
    processDict = dict()

    ################################
    ########### 需求预测 ############
    ################################
    '''
    未来各时段站点用户需求预测
    '''
    demand_pred = demandPred(staN,slotN,staFeaL,staTruthDemandL,processDict,evalDict,evalIndexList[1],
                             demandPreModel)
    
    ###################################
    ########### 站点状态评估 ###########
    ###################################
    '''
    站点电池调度数量范围计算
    '''
    # LR 左闭右闭
    LR,invalidStaIL = rebalancingRange_method2_multiFea(demand_pred,staTruthbatteryNL,staBatteryInfo,
                                               staTruthDemandL,processDict,evalDict,evalIndexList[2],
                                               batterNPreModel,staBatteryNFeaL)
#     print('invalidStaIL',invalidStaIL)
#     print("safeRange",LR)

    '''
    平衡区域需补电池数与可取电池数
    '''
    LR2 = exceptionBatteryNum(LR,processDict)

    '''
    确定需访问的站点
    '''
    LR2_v,disT_v,visitStaIL = confirmVisit(LR2,disT,processDict)

    ################################
    ########### 路径规划 ############
    ################################
    '''
    路径规划及站点电池调度数量确定
    '''
    # 核心算法 得到最佳站点访问路径及站点电池调度数量
    # [route,balanceNL] = SA(disT_v,C,r1,r2,LR2_v)
    [route,balanceNL] = SA_parallel(disT_v,C,r1,r2,LR2_v,processDict,evalDict,evalIndexList[3])

    # print('route',route)
    # print('balanceNL',balanceNL)

    routeTrue = []
    for j in range(len(route)):
        routeTrue.append(visitStaIL[route[j]]-1)
    processDict['routeTrue'] = str(routeTrue)

    # print(f'routeTrue: {routeTrue}')
    # print(f'balanceNL: {balanceNL}')
    
    # 进行场景模拟 计算用户需求满足百分比
    routeSimu = routeTrue[1:]
    balanceNLSimu = balanceNL[1:]
    simulationData = simulationDayData[testDay]
    a,b = scenario_simulation(simulationData,staBatteryInfo,routeSimu,balanceNLSimu,processDict,
                        evalDict,evalIndexList[4],evalIndexList[5],evalIndexList[6])
    allDN += a
    notSatN += b

    # 存储过程及结果文件
    processStaDict = dict()
    for j in range(len(processStaL)):
        processStaDict[processStaL[j]] = processDict[processStaL[j]]
    for j in range(len(processDayL)):
        if j>0:
            processAllDayDict[processDayL[j]].append(processDict[processDayL[j]])
    df1 = pd.DataFrame(processStaDict)
    df1.to_excel(f'localTest/result/simulation/process/{algName}/station/{algName}_sta_{testDay}.xlsx',index=False)

for i in range(len(evalIndexList)):
    if i==0:
        value = 'aver'
    elif i==4:
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
# # print(evalDict)

df1 = pd.DataFrame(processAllDayDict)
df1.to_excel(f'localTest/result/simulation/process/{algName}/{algName}_day_process.xlsx',index=False)        
df1 = pd.DataFrame(evalDict)
df1.to_excel(f'localTest/result/simulation/evaluation/{algName}_evaluation.xlsx',index=False)

t2 = time.time()
print(f"time cost: {t2-t1} s")