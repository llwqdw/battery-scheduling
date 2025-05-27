'''
评估线性站点需电池数预测的效果
'''

import sys
import copy
import pandas as pd
import numpy as np
import time
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error # 均方误差
from sklearn.metrics import mean_absolute_error # 平方绝对误差
from sklearn.metrics import r2_score # R square
import json
import joblib
from decimal import Decimal, ROUND_HALF_UP

# 模型评估函数 y_test 真实值列表 pred 预测值列表 model 模型名 file1 写入文件名
def evaluation(y_test, pred, model_name):
    rmse = mean_squared_error(y_test, pred, squared=False)
    mae = mean_absolute_error(y_test, pred)
    # r2 = r2_score(y_test,pred)

    print(model_name)
    print(f"Root Mean Squared Error (RMSE): {rmse}")
    print(f"Mean Absolute Error (MAE): {mae}")

    return rmse,mae

def dataStandard():
    demandData = json.load(open('dataExecute/data/normalData/demand_data_cd_20221201_20241009_1day.json','r')) # 需求数据
    demandSSL = list(demandData.values())
    dayL = list(demandData.keys())
    staN = len(demandSSL[0])
    # 读取站点每天需电池数数据
    batteryNDict = json.load(open('dataExecute/data/normalData/satisfiedBattertyNRsoc_cd_20221201_20241009.json','r'))

    standardData = [] # [预测站点需电池数 真实站点需电池数]
    for i in range(21,len(dayL)):
        dayStr = dayL[i]
        for j in range(staN):
            dayAllDemand = np.sum(np.array(demandSSL[i][j]))
            if dayAllDemand==0: # 站点一天没有换电需求的数据需去除
                continue
            list1 = []
            for k in range(1,8):
                list1.append(np.sum(np.array(demandSSL[i-k][j])))
            demandN = np.mean(np.array(list1))
            # 依据公司经验换电40次需8个电池 即换电5次需1个电池
            a = Decimal(f'{demandN/5}').quantize(Decimal('0'), rounding=ROUND_HALF_UP) # 四舍五入
            satisfiedBatteryN = max(int(a),0)
            truthN = batteryNDict[dayStr][j]
            standardData.append([satisfiedBatteryN,truthN])
    
    # 标准化数据文件
    arr1 = np.array(standardData)
    np.save('dataExecute/data/testData/company_satisfiedBattertyNum_standardData_20241009_1day.npy',arr1)
    print('dataStandard success')

def modelTest():
    standardData = np.load("dataExecute/data/testData/company_satisfiedBattertyNum_standardData_20241009_1day.npy")
    # print(standardData.shape)
    pred = standardData[:,0]
    Y = standardData[:,1]
    
    pred_train,pred_test,y_train,y_test = train_test_split(pred,Y,test_size =0.1,shuffle=True,random_state=42)

    # 评估站点需满足电池数预测效果
    model_name = "satisfiedBatteryNPre_linear"
    rmse,mae = evaluation(y_test,pred_test,model_name)

def companySaitifiedBatteryNPre(staN,demandHisL,staTruthbatteryNL,processDict,evalDict,evalIndex):
    satisfiedBatteryNL = []
    for i in range(staN):
        a = Decimal(f'{demandHisL[i]/4}').quantize(Decimal('0'), rounding=ROUND_HALF_UP) # 四舍五入
        satisfiedBatteryN = max(int(a),0)
        satisfiedBatteryNL.append(satisfiedBatteryN)

    # 评估站点需满足电池数预测效果
    model_name = "satisfiedBatteryNPre_linear"
    rmse,mae = evaluation(staTruthbatteryNL,satisfiedBatteryNL,model_name)

    processDict['satisfiedBatteryNPred'] = list(satisfiedBatteryNL)
    processDict['satisfiedBatteryNTruth'] = list(staTruthbatteryNL)
    evalDict[evalIndex].append([rmse,mae])

    return satisfiedBatteryNL

if __name__ == '__main__':
    # dataStandard()
    modelTest()