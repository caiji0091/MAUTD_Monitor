# coding=utf-8
import json
import requests
import time
import config
import datetime
from History_Data import History23_Data

MaxPri_li = []	#60天天最高价列表
MinPri_li = []	#60天最低价列表
for i in range(60):
    MaxPri_li.append(History23_Data[-60 + i][-1])
    MinPri_li.append(History23_Data[-60 + i][-2])

webhook = "https://open.feishu.cn/open-apis/bot/v2/hook/" + config.feishu_key	# 从config.py读取飞书的key
Gold_Pri = "http://web.juhe.cn/finance/gold/shgold?key=" + config.gold_key	# 从config.py读取gold数据的key


def Push_Msg(str):
    payload_message = {
        "msg_type": "text",
        "content": {
            "text": 'gold price --- ' + str
        }
    }
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("get", webhook, headers=headers, data=json.dumps(payload_message))
    print(response.text)


def Job():
    Newday_Flag = 1
    for i in range(27):
        Gold_Data = requests.get(Gold_Pri).json()['result'][0]['13']  # USE MAUTD DATA

        if Newday_Flag:
            MaxPri_li.append(float(Gold_Data['maxpri']))
            MaxPri_li.pop(0)
            MinPri_li.append(float(Gold_Data['minpri']))
            MinPri_li.pop(0)
            Newday_Flag = 0

        Msg = Gold_Data['variety'] + '\r\n' + Gold_Data['time'] + '\r\n\r\n newpri:' + Gold_Data[
            'latestpri'] + '\r\n maxpri:' + Gold_Data['maxpri'] + '\r\n minpri:' + Gold_Data[
                  'minpri'] + '\r\n yespri:' + Gold_Data['yespri'] + '\r\n\r\n'
        Msg = Msg + Anylyzer(float(Gold_Data['latestpri']), float(Gold_Data['maxpri']), float(Gold_Data['minpri']))
        Push_Msg(Msg)
        if float(datetime.datetime.now().strftime('%H.%M')) > 22.15:
            return 1
        time.sleep(1800)


def Anylyzer(newpri, maxpri, minpri):
    comment = {'0': '今日无事，勾栏听曲', '1': '<at user_id="all">所有人</at>粗大事啦，金价大变！！！',
               '2': '<at user_id="all">所有人</at>阿祖，收手吧，该出了，价格已经超过60天最低价10%！！！',
               '3': '<at user_id="all">所有人</at>老板，发财的机会来了，准备抄底了，价格已经低过60天最高价10%！！！'}	#还没用起来
    maxpri_D60 = max(MaxPri_li)
    minpri_D60 = min(MinPri_li)
    variance = []
    variance.append('{:.2%}'.format(1 - newpri / maxpri))
    variance.append('{:.2%}'.format(newpri / minpri - 1))
    variance.append('{:.2%}'.format(1 - newpri / maxpri_D60))
    variance.append('{:.2%}'.format(newpri / minpri_D60 - 1))
    res = "\r\n相对昨日最高价降幅为" + variance[0] + "\r\n相对昨日最低价涨幅为" + variance[
        1] + "\r\n相对60天最高价降幅为" + variance[2] + "\r\n相对60天最低价涨幅为" + variance[3]
    return res

def IsWorkingDay():
    x=requests.get('https://www.[xxxxxx].cn/workingday/api')	# 利用接口判断今天是否工作日（交易日）
    return x.json()['is_workingday']


if __name__ == '__main__':
    while 1:
        Time_Now = float(datetime.datetime.now().strftime('%H.%M'))
        if  Time_Now > 9.15 and Time_Now < 22:	# 定时任务，判断是否在交易时间内
            if IsWorkingDay:
                Job()
            else:
                time.sleep(86400)

        time.sleep(60)

