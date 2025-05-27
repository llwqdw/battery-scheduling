'''
确认每个站点的最佳再平衡电池个数
输入: 站点特定访问顺序 站点电池再平衡范围 货车容积
输出: 站点再平衡电池数量
'''

import sys

'''
LR 每个站点的再平衡范围
C 货车容积
'''
def balanceNumCalcu(LR,C):
    N = len(LR) # 站点个数
    costT = [[sys.maxsize for j in range(C+1)] for i in range(N)] # 初始化成本表
    balanceT = [['n' for j in range(C+1)] for i in range(N)] # 存储中间站点的再平衡电池数量结果
    mCost = sys.maxsize # 存储总成本
    mBalanceNL = '' # 存储站点的再平衡电池数量结果
    for k in range(LR[0][0],LR[0][1]+1): # 访问第一个站点必须是取出电池
        if k>=0:
            costT[0][k] = k
            balanceT[0][k] = f'n,{k}'
    for i in range(1,N):
        for j in range(0,C+1): # 遍历上一个站点的货车各种容积情况
            if costT[i-1][j]!=sys.maxsize:
                for k in range(LR[i][0],LR[i][1]+1):
                    if (j+k<0) or (j+k>C):
                        continue
                    else:
                        if abs(k)+costT[i-1][j]<costT[i][j+k]:
                            costT[i][j+k] = abs(k)+costT[i-1][j]
                            balanceT[i][j+k] = f'{balanceT[i-1][j]},{k}'
    for j in range(0,C+1):
        if costT[N-1][j]<mCost:
            mCost = costT[N-1][j]
            mBalanceNL = balanceT[N-1][j]

    # print(f'costT: {costT}')
    # print(f'balanceT: {balanceT}')
    # print(f'mCost: {mCost}')
    # print(f'mBlance: {mBalance}')

    if len(mBalanceNL)==0: # 该路线货车电池无法满足站点需求 不可行
        return [sys.maxsize,[]]

    strs = mBalanceNL.split(',')
    mBalanceNL = [int(strs[i]) for i in range(1,len(strs))]

    return [mCost,mBalanceNL]