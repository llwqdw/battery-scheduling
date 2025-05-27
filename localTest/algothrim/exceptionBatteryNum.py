import math
import copy

'''
若可取电池数<需补电池数 按站点需补电池数的权重进行站点需补电池数的减少
'''
def exceptionBatteryNum(LR,processDict):
    LR2 = copy.deepcopy(LR)
    availiableN = 0
    requireN = 0
    for i in range(len(LR2)):
        RV = LR2[i][1]
        if RV==0:
            continue
        elif RV<0:
            requireN += -RV
        else:
            availiableN += RV
    print('availiableN',availiableN,'requireN',requireN)
    
    requireNDecreaseL = [0 for i in range(len(LR2))] # 存储各需补电池站点需下调的补电池数
    decreaseN = max(requireN-availiableN,0) # 存储需下调的总补电池数
    if availiableN<requireN:
        decreaseNA = 0
        dotIL = [] # 存储补电池数减多了的站点索引
        for i in range(len(LR2)):
            RV = LR2[i][1]
            if RV<0:
                weight = -RV/requireN
                value = weight*decreaseN
                if not(value==int(value)): # value不为整数
                    dotIL.append(i)
                decreaseNA += math.ceil(value)
                requireNDecreaseL[i] = math.ceil(value)
                LR2[i][1] += math.ceil(value) # 站点需补电池数减少
                LR2[i][0] += math.ceil(value) # 站点需补电池数减少
        addN = decreaseNA-decreaseN # 减多的电池数
        for i in range(len(dotIL)):
            if addN<=0:
                break
            staI = dotIL[i]
            LR2[staI][1] -= 1 # 站点需补电池数增加
            LR2[staI][0] -= 1 # 站点需补电池数增加
            addN -= 1

    newAvailiableN = 0
    newRequireN = 0
    for i in range(len(LR2)):
        RV = LR2[i][1]
        if RV==0:
            continue
        elif RV<0:
            newRequireN += -RV
        else:
            newAvailiableN += RV
    print('newAvailN',newAvailiableN,'newRequireN',newRequireN)

    processDict['batteryAvailN,requireN,decreaseN,newAvailN,newRequireN'] =\
          str([availiableN,requireN,decreaseN,newAvailiableN,newRequireN])
    processDict['requireNDecrease'] = list(requireNDecreaseL)
    processDict['LR_2'] = list(LR2)
    return LR2