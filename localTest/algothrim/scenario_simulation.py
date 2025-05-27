'''
场景模拟 计算用户需求满足百分比
'''

'''
依据时段需求预测结果计算各站点再平衡安全范围
输入: 各时段需求预测结果 站点当前电池数 站点容量
输出: 站点再平衡安全范围
'''

import sys
import copy
import json
import numpy as np
import pandas as pd

valid_rsoc = 80 # 用户可换出电池电量

def scenario_simulation(simulationData,staBatteryInfo1,route,balanceNL,processDict,evalDict,evalIndex1,
                        evalIndex2,evalIndex3):
    if len(route)==0 or len(balanceNL)==0:
        print('未找到合适路径 站点无需进行电池调度 直接场景模拟')
    staBatteryInfo = copy.deepcopy(staBatteryInfo1)

    slot_unix = 5*60 # 单位时段长度 1h 可定为10min 5min
    slotN = len(simulationData[0])
    staN = len(staBatteryInfo)
    print('slotN',slotN,'staN',staN)

    invalidStaIL = [] # 存储未创建的站点索引 需求满足情况也表示为[0,0]
    for i in range(staN): # 遍历每个站点
        if staBatteryInfo[i][2]==0: # 站点容积为0默认未创建
            invalidStaIL.append(i)
    # 不在市区的站点无需考虑    
    farStaIL = [240,144,301,295,150,219,166,153,176,344,297,99,299,289,223,145,222,39,335]
    for index in farStaIL:
        if index not in invalidStaIL:
            invalidStaIL.append(index)
    
    for i in range(len(route)): # 依据调度情况对站点电池情况进行调整
        staI = route[i]
        preN = staBatteryInfo[staI][0]
        staBatteryInfo[staI][0] -= balanceNL[i]
        list1 = []
        for i in range(staBatteryInfo[staI][0]):
            if i<preN:
                list1.append(staBatteryInfo[staI][1][i])
            else:
                list1.append(100)
        staBatteryInfo[staI][1] = list1

    staValidBatteryL = [0 for i in range(staN)] # 实时存储站点可用电池数
    allDemandNL = [[0 for j in range(slotN)] for i in range(staN)]
    rsocL = []
    rsocAL = []
    notSatisfiedDemandNL = [[0 for j in range(slotN)] for i in range(staN)]

    # 站点表 站点电池个数固定
    battery_table = [[-1 for j in range(staBatteryInfo[i][0])] for i in range(staN)]
    for i in range(slotN): # 时段模拟
        for j in range(staN): # 遍历每个站点
            if j in invalidStaIL:
                continue
            if i==0:
                for k in range(staBatteryInfo[j][0]):
                    rsoc = staBatteryInfo[j][1][k]
                    battery_table[j][k] = rsoc
                    if rsoc>=valid_rsoc:
                        staValidBatteryL[j] += 1
            # 站点电池按电量从高到低排序
            battery_table[j].sort(reverse=True)

        # 用户在站点进行换电
        for j in range(staN):
            if j in invalidStaIL:
                continue
            demandN = len(simulationData[j][i])
            # 确认当前时段站点的可用电池满足用户需求的情况
            demandSitatuion = staValidBatteryL[j]-demandN
            allDemandNL[j][i] = demandN
            notSatisfiedDemandNL[j][i] = -min(demandSitatuion,0)
            for k in range(min(demandN,staBatteryInfo[j][0])):
                if battery_table[j][k]>=valid_rsoc:
                    rsocL.append(battery_table[j][k])
                    rsocAL.append(battery_table[j][k])
                    battery_table[j][k] = simulationData[j][i][k] # 用户换入电池 电量进行改变
                else:
                    rsocAL.append(valid_rsoc-1) # 若存在用户换不到电池 则默认换出电量为79
            for k in range(0,demandN-staBatteryInfo[j][0]):
                rsocAL.append(valid_rsoc-1) # 若存在用户换不到电池 则默认换出电量为79

        # 时段结束电池电量增加
        for j in range(staN):
            if j in invalidStaIL:
                continue
            staValidBatteryL[j] = 0
            for k in range(staBatteryInfo[j][0]):
                plus_rsoc = (slot_unix/60)*staBatteryInfo[j][3]
                if battery_table[j][k]+plus_rsoc>100:
                    now_rsoc = 100
                else:
                    now_rsoc = int(battery_table[j][k]+plus_rsoc)
                if now_rsoc>=valid_rsoc:
                    staValidBatteryL[j] += 1
                battery_table[j][k] = now_rsoc
                
    demandNSimu = np.sum(np.array(allDemandNL))
    notSatisfiedDemandNSimu = np.sum(np.array(notSatisfiedDemandNL))
    satisfiedPercentage = (demandNSimu-notSatisfiedDemandNSimu)/demandNSimu
    aveRsoc = np.mean(np.array(rsocL))
    aveRsocA = np.mean(np.array(rsocAL))

    processDict['demandNSimu'] = demandNSimu
    processDict['notSatisfiedDemandNSimu'] = notSatisfiedDemandNSimu
    evalDict[evalIndex1].append(satisfiedPercentage)
    evalDict[evalIndex2].append(aveRsoc)
    evalDict[evalIndex3].append(aveRsocA)
    print('demandN',demandNSimu,'notSatisfiedDemandN',notSatisfiedDemandNSimu,'satisfiedPercentage',satisfiedPercentage)

    return demandNSimu,notSatisfiedDemandNSimu

if __name__ == '__main__':
    dayFeaDict = np.load('dataStandard/apply/dayFeaDict_1h.npy', allow_pickle=True).item()
    dayStaBatteryDict = np.load('dataStandard/apply/dayStaBatteryDict_1h.npy', allow_pickle=True).item()
    testDayL = list(dayFeaDict.keys())
    for i in range(len(testDayL)):
        testDay = testDayL[i]

        staBatteryInfo = dayStaBatteryDict[testDay]
        processDict = dict()
        evalDict = dict()
        evalIndexList = [1,2,3,4,5]
        for evalIndex in evalIndexList:
            evalDict[evalIndex] = []
        routeTrue = [-1, 0, 14, 1, 128, 52, 5, 54, 51, 6, 7, 10, 277, 18, 19, 260, 141, 20, 22, 274, 25, 27, 32, 37, 38, 40, 53, 55, 57, 149, 60, 61, 66, 67, 68, 69, 72, 241, 73, 75, 76, 79, 90, 94, 106, 124, 129, 130, 134, 135, 330, 140, 191, 196, 220, 221, 242, 294, 249, 253, 282, 267, 290, 292, 310, 316, 320, 323, 326, 348, 2, 161, 41, 24, 3, 13, 9, 271, 107, 11, 12, 17, 173, 21, 28, 29, 34, 36, 42, 43, 333, 45, 269, 49, 50, 56, 58, 62, 314, 63, 230, 64, 65, 77, 78, 82, 85, 87, 91, 101, 102, 104, 105, 113, 114, 125, 154, 175, 343, 177, 182, 184, 188, 194, 201, 204, 208, 209, 210, 328, 211, 212, 234, 239, 245, 255, 259, 266, 268, 272, 278, 317, 327, 337, 341]
        histBestBalanceNL = [0, 4, 4, 3, 3, 3, 5, 2, 2, 3, 5, 3, 3, 5, 5, 3, 4, 3, 5, 3, 2, 3, 2, 3, 2, 6, 3, 4, 3, 3, 2, 2, 4, 2, 2, 2, 3, 3, 6, 2, 3, 4, 3, 3, 3, 3, 4, 4, 3, 3, 5, 3, 3, 3, 3, 3, 3, 3, 3, 4, 3, 5, 3, 3, 4, 3, 3, 3, 4, 5, -8, -5, -3, -7, -4, -6, -3, -3, -6, -1, -2, -1, -2, -2, -4, -3, -6, -2, -2, -7, -4, -6, -1, -6, -4, -2, -7, -3, -2, -1, -2, -1, -3, -2, -1, -1, -1, -3, -5, -6, -1, -3, -4, -7, -1, -2, -2, -3, -1, -2, -1, -2, -4, -1, -2, -2, -1, -4, -2, -2, -5, -4, -1, -2, -5, -2, -1, -2, -5, -6, -1, -1, -5, -2, -2]
        routeSimu = routeTrue[1:]
        balanceNLSimu = histBestBalanceNL[1:]
        # 存储仿真实验数据
        simulationDayData = json.load(open('data/demand_data_cd_20221201_20241009_5min.json','r'))
        # 进行场景模拟 计算用户需求满足百分比
        simulationData = simulationDayData[testDay]
        scenario_simulation(simulationData,staBatteryInfo,routeSimu,balanceNLSimu,processDict,evalDict,evalIndexList[4])
        break