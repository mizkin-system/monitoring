#!/usr/bin/env python
# coding: utf-8

import time
import csv
import subprocess
import pandas as pd


class QUESTION01:

    index = 1

    def __init__(self):
        self.index = 1

    def monitorLog(self, logFile):
        print(u"監視ファイル名は"+logFile)
        popen = subprocess.Popen('tail -f ' + logFile, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        pid = popen.pid
        df = pd.DataFrame({"ip": ["ipv4-with-prefix"], "time": ["YYYYMMDDhhmmss"]}, index=["index"])

        print('Popen.pid:' + str(pid))
        print("monitor start")

        while True:
            line = popen.stdout.readline().strip()
            if line:
                item_list = line.decode().split(",")
                if item_list[-1] == '-':
                    # タイムアウト時のデータ追加
                    df.loc[self.index] = [item_list[1], item_list[0]]
                    self.index = self.index + 1
                else:
                    if [item_list[1]] in df['ip'].unique():
                        # 故障状態のサーバ応答がありましたら、故障とみなし、データ出力する
                        print(u"故障状態のサーバアドレス："+item_list[1])
                        print(u"サーバの故障期間：" + (df[df.ip == item_list[1]]).values[0][1] + "~" + item_list[0])
                        with open('./question1.csv', 'a') as f:
                            writer = csv.writer(f)
                            writer.writerow([item_list[1], (df[df.ip == item_list[1]]).values[0][1] + "~" + item_list[0]])
                        # タイムアウト時のデータ削除
                        df = df[df.ip != item_list[1]]

            time.sleep(1)


if __name__ == "__main__":
    app = QUESTION01()
    app.monitorLog("ping.log")
