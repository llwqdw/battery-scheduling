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

def demandPred(staN,slotN,staFeaL,preModel):
    xgbModel = preModel
    X = staFeaL.reshape(staN*slotN,len(staFeaL[0][0]))
    pred = xgbModel.predict(X)
    for i in range(len(pred)):
        a = Decimal(f'{pred[i]}').quantize(Decimal('0'), rounding=ROUND_HALF_UP) # 四舍五入
        pred[i] = max(int(a),0)
    pred = np.array(pred,dtype=np.int)

    pred = pred.reshape(staN,slotN)

    return pred