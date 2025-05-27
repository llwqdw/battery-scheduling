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

'''
预测下一时间区间各时段的需求数量
'''

# 模型评估函数 y_test 真实值列表 pred 预测值列表 model 模型名
def evaluation(y_test, pred, model_name):
    rmse = mean_squared_error(y_test, pred, squared=False)
    mae = mean_absolute_error(y_test, pred)
    # r2 = r2_score(y_test,pred)

    print(model_name)
    print(f"Root Mean Squared Error (RMSE): {rmse}")
    print(f"Mean Absolute Error (MAE): {mae}")
    
    return rmse,mae

# Root Mean Squared Error (RMSE): 5.73560991164073
# Mean Absolute Error (MAE): 3.75743611227482
def modelTrain():
    standardData = np.load("dataExecute/data/modelData/demand_standardData.npy")
    # print(standardData.shape)
    X = standardData[:,0:len(standardData[0])-1]
    Y = standardData[:,len(standardData[0])-1]
    print(X.shape,Y.shape)
    x_train,x_test,y_train,y_test = train_test_split(X,Y,test_size =0.1,shuffle=True,random_state=42)
    xgbModel = xgb.XGBRegressor()
    xgbModel.fit(x_train,y_train)

    # 保存模型
    joblib.dump(xgbModel,'localTest/model/demandPredModel.joblib')

def modelTest():
    xgbModel = joblib.load('localTest/model/demandPredModel.joblib')
    standardData = np.load("dataExecute/data/modelData/demand_standardData.npy")
    # print(standardData.shape)
    X = standardData[:,0:len(standardData[0])-1]
    Y = standardData[:,len(standardData[0])-1]
    # print(X.shape,Y.shape)
    x_train,x_test,y_train,y_test = train_test_split(X,Y,test_size =0.1,shuffle=True,random_state=42)
    pred = xgbModel.predict(x_test)

    for i in range(len(pred)):
        a = Decimal(f'{pred[i]}').quantize(Decimal('0'), rounding=ROUND_HALF_UP) # 四舍五入
        pred[i] = max(int(a),0)
    pred = np.array(pred,dtype=np.int)
    # print("x_test",x_test)
    print("y_test",y_test)
    print("pred",pred)
    
    biasNum = np.sum(np.abs(np.array(pred)-np.array(y_test)))
    print("biasNum",biasNum)

    model_name = "demandPre_xgboost"
    rmse,mae = evaluation(y_test,pred,model_name)

def demandPred(staN,slotN,staFeaL,staTruthDemandL,processDict,evalDict,evalIndex,preModel):
    xgbModel = preModel
    X = staFeaL.reshape(staN*slotN,len(staFeaL[0][0]))
    Y = staTruthDemandL.reshape(staN*slotN)
    pred = xgbModel.predict(X)
    for i in range(len(pred)):
        a = Decimal(f'{pred[i]}').quantize(Decimal('0'), rounding=ROUND_HALF_UP) # 四舍五入
        pred[i] = max(int(a),0)
    pred = np.array(pred,dtype=np.int)
    # print("x_test",X)
    # print("y_test",Y)
    # print("pred",pred)

    model_name = "demandPre_xgboost"
    rmse,mae = evaluation(Y,pred,model_name)

    processDict['demandPre'] = list(pred.reshape(staN,slotN))
    processDict['demandTruth'] = list(Y.reshape(staN,slotN))
    evalDict[evalIndex].append([rmse,mae])

    pred = pred.reshape(staN,slotN)

    return pred

# 对用户需求预测模型进行训练
if __name__ == '__main__':
    modelTrain()
    modelTest()