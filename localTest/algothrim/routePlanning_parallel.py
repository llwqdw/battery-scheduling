import sys
import os
sys.path.append(os.path.abspath(os.path.join(sys.path[0], '..')))
import pandas as pd
import numpy as np
import math
import random
import copy
import time
from algothrim.balanceNumCalcu import balanceNumCalcu

'''
电池调度系统核心算法
确认最佳站点访问顺序及每个站点的最佳再平衡电池个数
输入: 站点距离表 站点电池再平衡范围 站点容积 货车容积
输出: 最佳站点访问顺序 站点再平衡电池数量
'''

def SA_parallel(disT,C,r1,r2,LR,processDict,evalDict,evalIndex):
    t1 = time.time()

    posStas = [] # 存储存在多余电池的站点索引
    for i in range(1,len(LR)):
        if LR[i][1]>0:
            posStas.append(i)

    # 产生初始解
    bestRoute = iniRouteFunc3(disT,LR,posStas,C)
    [bestProfit, bestDist, bestBalance] = evalFunc(bestRoute,disT,LR,C,r1,r2)
    histBestProfit = bestProfit
    histBestRoute = bestRoute
    histBestDist = bestDist
    histBestBalanceNL = bestBalance

    distSum = sum(histBestDist)
    balanceSum = sum(histBestBalanceNL)
    balanceAbsSum = 0
    for balance in histBestBalanceNL:
        balanceAbsSum += abs(balance)
    
    processDict['distSum'] = distSum
    processDict['balanceSum'] = balanceSum
    processDict['balanceAbsSum'] = balanceAbsSum
    processDict['histBestDist'] = str(histBestDist)
    processDict['histBestBalanceNL'] = str(histBestBalanceNL)
    evalDict[evalIndex].append([distSum,balanceAbsSum])

    return histBestRoute,histBestBalanceNL

'''
初始化贪心解
依次加入离前一个站点最近且货车电池数可满足站点调度需求的站点
(若站点最大容积为C 货车容积>=2C-2 则一定为可行解 因为最差情况下站点需补C个电池
货车从两个可取电池为C-1的站点取电池就可满足需求)
'''
def iniRouteFunc3(disT,LR,posStas,C):
    route = [0] # 仓库第一个访问
    truckBatteryN = 0
    while len(route)<len(LR):
        lastS = route[len(route)-1]
        candi = []
        for j in range(len(LR)):
            if j not in route:
                candi.append(j)
        minDis = sys.maxsize
        minSta = -1
        minVary = 0
        for index in candi:
            # 若货车电池数不满足站点调度需求 该站点暂时不考虑
            varyN = LR[index][1]
            if (varyN<0 and truckBatteryN+varyN<0) or (varyN>0 and truckBatteryN+varyN)>C:
                continue
            if disT[lastS][index]<minDis:
                minDis = disT[lastS][index]<minDis
                minSta = index
                minVary = varyN
        newS = minSta
        truckBatteryN += minVary
        route.append(newS)
    return route

'''
评估规划方案
总成本=货车运输成本+电池调度成本
'''
def evalFunc(route,disT,LR,C,r1,r2):
    distL = [] # 存储路线中各站点的距离列表
    distanceCost = 0 # 货车运输成本

    for i in range(0,len(route)-1):
        dist = disT[route[i]][route[i+1]]
        distanceCost += dist
        distL.append(dist)
    distanceCost += disT[route[len(route)-1]][0] # 加上最后站点到仓库的距离
    distL.append(disT[route[len(route)-1]][0])

    newLR = []
    for index in route:
        newLR.append(LR[index])
    [mCost,mBalanceNL] = balanceNumCalcu(newLR,C) # 计算最佳站点电池调度数

    if mCost==sys.maxsize: # 特定路径不存在站点电池数解
        return [-sys.maxsize,distL,mBalanceNL]
    
    balanceCost = mCost # 电池调度成本

    allCost = distanceCost*r1+balanceCost*r2 # 度量统一化
    profit = -allCost # 返回收益(与成本相反)
    return [profit,distL,mBalanceNL]