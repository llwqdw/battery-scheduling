import numpy as np
import joblib
import xgboost as xgb
from sklearn.ensemble import GradientBoostingRegressor

# 训练用户需求预测模型
def demandPreModelTrain():
    standardData = np.load("dataExecute/data/modelData/demand_standardData.npy")
    X = standardData[:,0:len(standardData[0])-1]
    Y = standardData[:,len(standardData[0])-1]

    xgbModel = xgb.XGBRegressor()
    xgbModel.fit(X,Y)

    # 保存模型
    joblib.dump(xgbModel,'businessApplication/model/demandPredModel.joblib')
    print('complete!')

# 训练需电池数预测模型
def satisfiedBattertyNumPreModelTrain():
    standardData = np.load("dataExecute/data/modelData/satisfiedBattertyN_standardData.npy")
    X = standardData[:,0:len(standardData[0])-1]
    Y = standardData[:,len(standardData[0])-1]

    xgbModel = GradientBoostingRegressor()
    xgbModel.fit(X,Y)

    # 保存模型
    joblib.dump(xgbModel,'businessApplication/model/satisfiedBattertyNPredModel.joblib')
    print('complete!')

demandPreModelTrain()
satisfiedBattertyNumPreModelTrain()