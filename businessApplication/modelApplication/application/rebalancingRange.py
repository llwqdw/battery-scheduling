'''
依据时段需求预测结果计算各站点再平衡安全范围 XGBoost模型预测
输入: 各时段需求预测结果 站点当前电池数 站点容量
输出: 站点再平衡安全范围
'''

import sys
import copy
import pandas as pd
import numpy as np
import time
import xgboost as xgb
from sklearn.ensemble import GradientBoostingRegressor
import json
import joblib
from decimal import Decimal, ROUND_HALF_UP

def satisfiedBatteryNPred(demand_pred,preModel,staBatteryNFeaL):
    standData = []
    for i in range(len(demand_pred)):
        list1 = list(demand_pred[i])
        sum = np.sum(np.array(list1))
        list2 = [sum]+list(staBatteryNFeaL[i]) # 拼总需求数
        standData.append(list2)
    xgbModel = preModel
    standardData = np.array(standData)
    X = standardData
    pred = xgbModel.predict(X)

    for i in range(len(pred)):
        a = Decimal(f'{pred[i]}').quantize(Decimal('0'), rounding=ROUND_HALF_UP) # 四舍五入
        pred[i] = max(int(a),0)
    pred = np.array(pred,dtype=np.int)

    return pred

def rebalancingRange(demand_pred,staBatteryInfo,preModel,staBatteryNFeaL):
    staN = len(staBatteryInfo)

    predL = satisfiedBatteryNPred(demand_pred,preModel,staBatteryNFeaL)
    staBatteryNL = [staBatteryInfo[i][0] for i in range(staN)] # 存储站点电池数
    minDemandSitatuionL = [staBatteryNL[i]-predL[i] for i in range(staN)]
    LR = [[] for j in range(staN)]
    for j in range(staN):
        minSituation = minDemandSitatuionL[j]
        if minSituation==0:
            LR[j] = [0,0] # 不可调度
        elif minSituation<0:
            if -minSituation+staBatteryInfo[j][0]>staBatteryInfo[j][1]: # 需补电池数最多为C-N
                minSituation = staBatteryInfo[j][0]-staBatteryInfo[j][1]
            LR[j] = [minSituation,minSituation] # 需补电池-min个
        else:
            LR[j] = [0,minSituation] # 可取最多min个电池

    return predL,LR