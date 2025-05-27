import requests
import json
import pandas as pd
import math
import time

def wea_prediciton():
    # ldh: F63BZ-OINK4-YRLUB-KQNGL-YZHMF-DBFSS

    list1 = []

    key = 'F63BZ-OINK4-YRLUB-KQNGL-YZHMF-DBFSS'

    base_url = f"https://apis.map.qq.com/ws/weather/v1/?key={key}&adcode=510100&type=future"
    response_data = requests.get(base_url).text
    responseDict = eval(response_data)

    dicting = responseDict['result']['forecast'][0]['infos'][0]
    dict1 = dict()
    dict1['城市']='成都市';dict1['日期']=f"{dicting['date']} {dicting['week']}"
    dict1['最高温度']=f"{dicting['day']['temperature']}℃"
    dict1['最低温度']=f"{dicting['night']['temperature']}℃"
    dict1['天气']=dicting['day']['weather'];dict1['风向']=dicting['day']['wind_power']
    list1.append(dict1)
    df1 = pd.DataFrame(list1)
    df1.to_excel(f'dataExecute/data/applicationData/wea_prediction.xlsx', index=False)

if __name__ == '__main__':
    wea_prediciton()