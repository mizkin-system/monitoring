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
    # 直近応答回数
    recent_respond_times = 1
    # 平均応答時間
    average_respond_mini_seconds = 100

    def __init__(self, args):
        self.timeout_times = int(args.timeout_times)
        self.recent_respond_times = int(args.recent_respond_times)
        self.average_respond_mini_seconds = int(args.average_respond_mini_seconds)
        print("timeout_times={}".format(self.timeout_times))
        print("recent_respond_times={}".format(self.recent_respond_times))
        print("average_respond_mini_seconds={}".format(self.average_respond_mini_seconds))
        self.index = 1
        self.index_respond = 1

    def monitorLog(self, logFile):
        print(u"監視ファイル名は"+logFile)
        popen = subprocess.Popen('tail -f ' + logFile, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        pid = popen.pid
        df = pd.DataFrame({"ip": ["ipv4-with-prefix"], "time": ["YYYYMMDDhhmmss"]}, index=["index"])
        df_respond = pd.DataFrame({"ip": ["ipv4-with-prefix"], "time": ["YYYYMMDDhhmmss"], "respond_mini_seconds": ["fff"]}, index=["index"])

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
                    if (df[df.ip == item_list[1]])["ip"].size >= int(self.timeout_times):
                        # 故障状態のサーバ応答がありましたら、故障とみなし、データ出力する
                        print(u"故障状態のサーバアドレス："+item_list[1])
                        print(u"サーバの故障期間：" + (df[df.ip == item_list[1]]).values[0][1] + "~" + item_list[0])
                        with open('./question3.csv', 'a') as f:
                            writer = csv.writer(f)
                            writer.writerow([item_list[1], (df[df.ip == item_list[1]]).values[0][1] + "~" + item_list[0]])
                    # タイムアウト時のデータ削除
                    df = df[df.ip != item_list[1]]

                    # 応答時のデータ追加
                    df_respond.loc[self.index_respond] = [item_list[1], item_list[0], item_list[2]]
                    self.index_respond = self.index_respond + 1
                    totle_mini_seconds = 0
                    self.recent_respond_times = int(self.recent_respond_times)
                    df_respond_ip_size = len((df_respond[df_respond.ip == item_list[1]]).values)
                    recent_start_index = df_respond_ip_size - self.recent_respond_times
                    if df_respond_ip_size >= self.recent_respond_times:
                        recent_respond_list = (df_respond[df_respond.ip == item_list[1]])["respond_mini_seconds"][recent_start_index:]
                        for recent_respond in recent_respond_list:
                            totle_mini_seconds = totle_mini_seconds + int(recent_respond)
                        if totle_mini_seconds > self.average_respond_mini_seconds:
                            print(u"サーバの過負荷状態となっている期間を出力する")
                            df_recent = ((df_respond[df_respond.ip == item_list[1]])[recent_start_index:]).copy(deep=True)
                            with open('./question3_overload.csv', 'a') as f:
                                writer = csv.writer(f)
                                writer.writerow([item_list[1], df_recent.iloc[0, 1] + "~" + item_list[0]])
                            df_respond = df_respond[df_respond.ip != item_list[1]]
                            df_respond = df_respond.append(df_recent)
            time.sleep(1)


if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(exit_on_error=False)
        parser.add_argument('timeout_times')
        parser.add_argument('recent_respond_times')
        parser.add_argument('average_respond_mini_seconds')
        args = parser.parse_args()
        app = QUESTION03(args)
        app.monitorLog("ping.log")
    except KeyboardInterrupt:
        print(u"monitor end")
    except SystemExit:
        print(u"引数設定不正で異常終了しました。引数をご確認ください。")
    except Exception as e:
        print(u"異常終了しました。")
        print(e)
