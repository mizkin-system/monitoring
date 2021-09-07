#!/usr/bin/env python
# coding: utf-8

import time
import csv
import subprocess
import pandas as pd
import argparse


class QUESTION03:

    index = 1
    index_respond = 1
    timeout_times = 1
    respond_times = 1
    respond_mini_seconds = 100

    def __init__(self, args):
        self.timeout_times = args.timeout_times
        self.respond_times = args.respond_times
        self.respond_mini_seconds = args.respond_mini_seconds
        print('respond_mini_seconds=' + self.respond_mini_seconds)
        print('timeout_times=' + self.timeout_times)
        print('respond_times=' + self.respond_times)
        self.index = 1
        self.index_respond = 1

    def monitorLog(self, logFile):
        print(u"監視ファイル名は"+logFile)
        popen = subprocess.Popen('tail -f ' + logFile, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        pid = popen.pid
        df = pd.DataFrame({"ip": ["ipv4-with-prefix"], "time": ["YYYYMMDDhhmmss"]}, index=["index"])
        df_respond = pd.DataFrame({"ip": ["ipv4-with-prefix"], "respond_mini_seconds": ["fff"]}, index=["index"])

        print('Popen.pid:' + str(pid))
        print("monitor start")

        while True:
            line = popen.stdout.readline().strip()
            if line:
                item_list = line.decode().split(",")
                if item_list[-1] == '-':
                    # 最初タイムアウト時のデータ追加
                    df.loc[self.index] = [item_list[1], item_list[0]]
                    self.index = self.index + 1
                else:
                    df_respond[self.index] = [item_list[1], item_list[2]]
                    totle_mini_seconds = 0
                    if len((df_respond[df_respond.ip == [1]]).values) >= self.respond_times:
                        respond_list = (df_respond[df_respond.ip == [1]])["respond_mini_seconds"]
                        print(respond_list)
                        for i in range(-self.respond_times, -1):
                            totle_mini_seconds = totle_mini_seconds + respond_list[i]
                            print(i)
                            print(respond_list[i])
                        if totle_mini_seconds > self.respond_mini_seconds:
                            print("question3 サーバの負荷状態となっている期間を出力する")

                    if len((df[df.ip == [1]]).values) >= self.timeout_times:
                        # 故障状態のサーバ応答がありましたら、故障とみなし、データ出力する
                        print(u"故障状態のサーバアドレス："+item_list[1])
                        print(u"サーバの故障期間：" + (df[df.ip == item_list[1]]).values[0][1] + "~" + item_list[0])
                        with open('./question3.csv', 'a') as f:
                            writer = csv.writer(f)
                            writer.writerow([item_list[1], (df[df.ip == item_list[1]]).values[0][1]] + "~" + item_list[0])
                    # 故障状態のデータ削除
                    df = df[df.ip != item_list[1]]

            time.sleep(1)


if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(exit_on_error=False)
        parser.add_argument('timeout_times')
        parser.add_argument('respond_times')
        parser.add_argument('respond_mini_seconds')
        args = parser.parse_args()
        app = QUESTION03(args)
        app.monitorLog("ping.log")
    except BaseException:
        print(u"引数設定不正で異常終了しました。引数をご確認ください。")
