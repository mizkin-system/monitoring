#!/usr/bin/env python
# coding: utf-8

import time
import csv
import subprocess
import pandas as pd
import argparse
import ipaddress


class QUESTION04:

    index = 1
    timeout_times = 1

    SUB_NET_IP1 = "192.168.11.0/30"
    SUB_NET_IP2 = "192.168.10.0/30"

    def __init__(self, timeout_times):
        self.timeout_times = timeout_times
        print('timeout_times=' + self.timeout_times)
        self.index = 1

    def monitorLog(self, logFile):
        print(u"監視ファイル名は"+logFile)
        popen = subprocess.Popen('tail -f ' + logFile, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        pid = popen.pid
        df = pd.DataFrame({"ip": ["ipv4"], "time": ["YYYYMMDDhhmmss"], "subnet": ["0.0.0.0/0"]}, index=["index"])

        # サブネット定義
        sub_net1 = list(ipaddress.ip_network(self.SUB_NET_IP1).hosts())
        sub_net2 = list(ipaddress.ip_network(self.SUB_NET_IP2).hosts())

        print('Popen.pid:' + str(pid))
        print("monitor start")

        while True:
            line = popen.stdout.readline().strip()
            if line:
                item_list = line.decode().split(",")
                ip_address = item_list[1].split('/')[0]
                if item_list[-1] == '-':
                    # タイムアウト時のデータ追加
                    if ipaddress.IPv4Address(ip_address) in sub_net1:
                        df.loc[self.index] = [ip_address, item_list[0], self.SUB_NET_IP1]
                    elif ipaddress.IPv4Address(ip_address) in sub_net2:
                        df.loc[self.index] = [ip_address, item_list[0], self.SUB_NET_IP2]
                    else:
                        df.loc[self.index] = [ip_address, item_list[0], "0.0.0.0/0"]
                    self.index = self.index + 1
                else:
                    # サブネット障害判定
                    df = self.check_subnet_error(ip_address, sub_net1, df)
                    df = self.check_subnet_error(ip_address, sub_net2, df)

                    if (df[df.ip == ip_address])["ip"].size >= int(self.timeout_times):
                        # 故障状態のサーバ応答がありましたら、故障とみなし、データ出力する
                        print(u"故障状態のサーバアドレス："+ip_address)
                        print(u"サーバの故障期間：{}".format((df[df.ip == ip_address]).values[0][1] + "~" + item_list[0]))
                        with open('./question4_server_error.csv', 'a') as f:
                            writer = csv.writer(f)
                            writer.writerow([item_list[1], (df[df.ip == ip_address]).values[0][1] + "~" + item_list[0]])
                    # タイムアウト時のデータ削除
                    df = df[df.ip != ip_address]
            # print(df)
            time.sleep(1)

    def check_subnet_error(self, ip_address, sub_net, df):
        is_subnet1_error = True
        if ipaddress.IPv4Address(ip_address) in sub_net:
            for ip in sub_net:
                if (df[df.ip == str(ip)]).size < int(self.timeout_times):
                    is_subnet1_error = False
                    break
            if is_subnet1_error:
                subnet = (df[df.ip == ip_address]).iloc[0, 2]
                print(u"障害サブネット：{}".format(subnet))
                with open('./question4_subnet_error.csv', 'a') as f:
                    writer = csv.writer(f)
                    writer.writerow([subnet, (df[df.ip == ip_address]).iloc[0, 1] + "~" + (df[df.ip == ip_address]).iloc[-1, 1]])
                df = df[df.subnet != subnet]
        return df


if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('timeout_times')
        args = parser.parse_args()
        app = QUESTION04(args.timeout_times)
        app.monitorLog("ping.log")
    except KeyboardInterrupt:
        print(u"monitor end")
    except SystemExit:
        print(u"引数設定不正で異常終了しました。引数をご確認ください。")
    except Exception as e:
        print(u"異常終了しました。")
        print(e)
