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
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error # 均方误差
from sklearn.metrics import mean_absolute_error # 平方绝对误差
from sklearn.metrics import r2_score # R square
import json
import joblib
from decimal import Decimal, ROUND_HALF_UP

# 模型评估函数 y_test 真实值列表 pred 预测值列表 model 模型名
def evaluation(y_test, pred, model_name):
    rmse = mean_squared_error(y_test, pred, squared=False)
    mae = mean_absolute_error(y_test, pred)
    # r2 = r2_score(y_test,pred)

    print(model_name)
    print(f"Root Mean Squared Error (RMSE): {rmse}")
    print(f"Mean Absolute Error (MAE): {mae}")

    return rmse,mae

def modelTrain():
    standardData = np.load("dataExecute/data/modelData/satisfiedBattertyN_standardData.npy")
    X = standardData[:,0:len(standardData[0])-1]
    Y = standardData[:,len(standardData[0])-1]
    print(X.shape,Y.shape)
    x_train,x_test,y_train,y_test = train_test_split(X,Y,test_size =0.1,shuffle=True,random_state=42)
    # xgbModel = xgb.XGBRegressor()
    xgbModel = GradientBoostingRegressor() # 0.8748 预测需电池数特征为预测需求特征
    # 0.5256 预测需电池数特征为总预测需求数及预测需求特征
    xgbModel.fit(x_train,y_train)

    # 保存模型
    joblib.dump(xgbModel,'localTest/model/satisfiedBattertyNPredModel.joblib')

def modelTest():
    xgbModel = joblib.load('localTest/model/satisfiedBattertyNPredModel.joblib')
    standardData = np.load("dataExecute/data/modelData/satisfiedBattertyN_standardData.npy")
    X = standardData[:,0:len(standardData[0])-1]
    Y = standardData[:,len(standardData[0])-1]
    # print(X.shape,Y.shape)
    x_train,x_test,y_train,y_test = train_test_split(X,Y,test_size=0.1,shuffle=True,random_state=42)
    pred = xgbModel.predict(x_test)

    for i in range(len(pred)):
        a = Decimal(f'{pred[i]}').quantize(Decimal('0'), rounding=ROUND_HALF_UP) # 四舍五入
        pred[i] = max(int(a),0)
    pred = np.array(pred,dtype=np.int)
    # print("x_test",x_test)
    # print("y_test",y_test)
    # print("pred",pred)

    # dict1 = {'pred': pred, 'truth': y_test}
    # df1 = pd.DataFrame(dict1)
    # df1.to_excel("1.xlsx",index=False)

    model_name = "satisfiedBatteryNPre_gbrt"
    rmse,mae = evaluation(y_test,pred,model_name)

def satisfiedBatteryNPred(demand_pred,staTruthbatteryNL,staTruthDemandL,processDict,evalDict,
                          evalIndex,preModel,staBatteryNFeaL):
    standData = []
    for i in range(len(demand_pred)):
        list1 = list(demand_pred[i])
        sum = np.sum(np.array(list1))
        list2 = [sum]+list(staBatteryNFeaL[i]) # 拼总需求数
        # list2 = list(staBatteryNFeaL[i]) # 不拼总需求数
        standData.append(list2)
    staTruthDemandL2 = []
    for i in range(len(staTruthDemandL)):
        list1 = list(staTruthDemandL[i])
        sum = np.sum(np.array(list1))
        list2 = list1+[sum]
        staTruthDemandL2.append(list2)
    xgbModel = preModel
    standardData = np.array(standData)
    X = standardData
    Y = staTruthbatteryNL
    pred = xgbModel.predict(X)

    for i in range(len(pred)):
        a = Decimal(f'{pred[i]}').quantize(Decimal('0'), rounding=ROUND_HALF_UP) # 四舍五入
        pred[i] = max(int(a),0)
    pred = np.array(pred,dtype=np.int)
    # print("x_test",X)
    # print("y_test",Y)
    # print("pred",pred)

    model_name = "satisfiedBatteryNPre_xgboost"
    rmse,mae = evaluation(Y,pred,model_name)

    processDict['satisfiedBatteryNInput'] = list(standData)
    processDict['satisfiedBatteryNInputTruth'] = list(staTruthDemandL2)
    processDict['satisfiedBatteryNPred'] = list(pred)
    processDict['satisfiedBatteryNTruth'] = list(Y)
    evalDict[evalIndex].append([rmse,mae])

    return pred

def rebalancingRange_method2_multiFea(demand_pred,staTruthbatteryNL,staBatteryInfo,staTruthDemandL,processDict,
                             evalDict,evalIndex,preModel,staBatteryNFeaL):
    staN = len(staBatteryInfo)

    invalidStaIL = [] # 存储未创建的站点索引 需求满足情况也表示为[0,0]
    for i in range(staN): # 遍历每个站点
        if staBatteryInfo[i][2]==0: # 站点容积为0默认未创建
            invalidStaIL.append(i)
    # 不在市区的站点无需考虑
    farStaIL = [240,144,301,295,150,219,166,153,176,344,297,99,299,289,223,145,222,39,335]
    for index in farStaIL:
        if index not in invalidStaIL:
            invalidStaIL.append(index)

    predL = satisfiedBatteryNPred(demand_pred,staTruthbatteryNL,staTruthDemandL,processDict,
                                  evalDict,evalIndex,preModel,staBatteryNFeaL)
    staBatteryNL = [staBatteryInfo[i][0] for i in range(staN)] # 存储站点电池数
    minDemandSitatuionL = [staBatteryNL[i]-predL[i] for i in range(staN)]
    for index in invalidStaIL:
        minDemandSitatuionL[index] = 0
    LR = [[] for j in range(staN)]
    for j in range(staN):
        minSituation = minDemandSitatuionL[j]
        if minSituation==0:
            LR[j] = [0,0] # 不可调度
        elif minSituation<0:
            if -minSituation+staBatteryInfo[j][0]>staBatteryInfo[j][2]: # 需补电池数最多为C-N
                minSituation = staBatteryInfo[j][0]-staBatteryInfo[j][2]
            LR[j] = [minSituation,minSituation] # 需补电池-min个
        else:
            LR[j] = [0,minSituation] # 可取最多min个电池

    isValidL = [1 for i in range(staN)]
    for index in invalidStaIL:
        isValidL[index] = 0
    processDict['isValid'] = list(isValidL)
    processDict['staBatteryN'] = list(staBatteryNL)
    processDict['LR_1'] = list(LR)
    return LR,invalidStaIL

# 对站点需电池数预测模型进行训练
if __name__ == '__main__':
    modelTrain()
    modelTest()