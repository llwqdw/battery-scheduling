'''
优先将可取电池数大的可取电池站点作为访问站点
生成访问站点与原始站点索引映射
'''
def confirmVisit(LR,disT,processDict):
    visitStaIL = [0] # 初始化仓库点访问
    availStaDict = dict()
    requireN = 0
    visitAvailN = 0
    for i in range(1,len(LR)+1): # 由于考虑仓库 站点索引从1开始
        RV = LR[i-1][1]
        if RV<0:
            visitStaIL.append(i) # 站点索引从1开始 还原时LR注意-1
            requireN += -RV
        elif RV>0:
            availStaDict[i] = RV
    sorted_list = sorted(availStaDict.items(), key=lambda x:x[1],reverse=True)
    for i in range(len(sorted_list)):
        if visitAvailN>=requireN:
            break
        visitAvailN += sorted_list[i][1]
        visitStaIL.append(sorted_list[i][0])
    print('visitAvailN',visitAvailN,'requireN',requireN)
    visitStaIL.sort()
    visitStaN = len(visitStaIL) # 包含仓库

    LR_v = [[0,0]] # 仓库需求默认为0
    for i in range(1,visitStaN):
        LR_v.append(LR[visitStaIL[i]-1]) # 站点索引从1开始 LR注意-1
    
    disT_v = [[0 for j in range(visitStaN)] for i in range(visitStaN)]
    for i in range(visitStaN):
        for j in range(visitStaN):
            disT_v[i][j] = disT[visitStaIL[i]][visitStaIL[j]]

    isVisitL = [0 for i in range(len(LR))]
    for visitI in visitStaIL:
        isVisitL[visitI-1] = 1
    processDict['isVisit'] = list(isVisitL)
    processDict['visitAvailN,visitStaN'] = str([visitAvailN,visitStaN])

    return LR_v,disT_v,visitStaIL