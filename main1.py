import json
import os
from time import sleep
import threading

import serial  # 导入串口通信库
import struct
import re

ser = serial.Serial()


class MyThread(threading.Thread):
    def __init__(self, ser):
        super().__init__()
        self.ser = ser

    def hexShow(self, argv):

        result = ''
        for i in range(len(argv)):
            hvol = argv[i]
            hhex = '%02dx' % hvol
            result += hhex + ' '
        return result

    def run(self):
        while True:
            global stop_Threads
            if ser.in_waiting:
                data = ser.read_all()
                # data = data.decode('ascii', errors='ignore')
                data1 = self.hexShow(data)
                data_decode = data1.split(' ')
                if len(data_decode) > 8:
                    match = re.match(r"(\d+)\D+", data_decode[8])
                    power = int(match.group(1))
                    # print(data_decode)
                    print('当前的电量是  ', power)

            if stop_Threads:
                break


def port_open_recv():  # 对串口的参数进行配置
    ser.port = 'COM12'
    ser.baudrate = 9600
    ser.bytesize = 8
    ser.stopbits = 1
    ser.parity = "N"  # 奇偶校验位
    ser.open()
    ser.timeout = 5
    if (ser.isOpen()):
        print("串口打开成功！")
    else:
        print("串口打开失败！")


# isOpen()函数来查看串口的开闭状态

def port_close():
    ser.close()
    if (ser.isOpen()):
        print("串口关闭失败！")
    else:
        print("串口关闭成功！")


def send(send_data):
    if (ser.isOpen()):
        ser.write(send_data)  # 编码
        print("发送成功", send_data)
    else:
        print("发送失败！")


# 计数循环次数，次数到了停止
def rotate(n):  # 控制循环次数
    sending1 = "00 01 04 A5 5A 08 23 87 01 00 b2"
    sending2 = "00 01 04 A5 5A 08 23 87 04 00 b5"
    sending1 = bytes.fromhex(sending1)
    send(sending1)
    sleep(n * 21)
    sending2 = bytes.fromhex(sending2)
    send(sending2)


# 计算校验和
def checksum(temp1, temp2):
    temp = "1A7"
    temp = int(temp, 16)
    temp1 = int(temp1, 16)
    temp2 = int(temp2, 16)
    temp += (temp1 + temp2)
    res = hex(temp)[2:]
    res = res.rjust(4, "0")
    return res[2:]


# 设置速度
def speedSet(speed):
    hexSpeed = hex(speed)[2:]
    res = hexSpeed.rjust(4, "0")
    # print(res, len(res))
    temp1 = res[0:2]
    temp2 = res[2:]
    inst = "00 01 04 A5 5A 08 23 7d"
    instlist = inst.split(' ')
    instlist.insert(8, temp2)
    instlist.insert(9, temp1)
    instlist.insert(10, checksum(temp1, temp2))
    speedSend = " ".join(instlist)
    return speedSend


# 读取JSON文件
def load(file_name):
    if os.path.exists(file_name):
        f = open(file_name, encoding='utf-8')
        content = f.read()
        user_dic = json.loads(content)
        return user_dic


# # 读取文本内容到列表
# with open("123.txt", "r", encoding='utf-8') as file:
#     for line in file:
#         line = line.strip('\n')  # 删除换行符
#         SaveList.append(line)
#     file.close()

# 目标站点命令
my_dict = {1: "00 01 04 A5 5A 08 23 9D 01 00 C8",
           2: "00 01 04 A5 5A 08 23 9D 02 00 C9",
           3: "00 01 04 A5 5A 08 23 9D 03 00 CA",
           4: "00 01 04 A5 5A 08 23 9D 04 00 CB",
           5: "00 01 04 A5 5A 08 23 9D 05 00 CC"}

if __name__ == '__main__':
    port_open_recv()

    while True:
        flag = int(input(
            "请输入您的选择：1.前往目标站点 2.读取文件中的指令 3.设置小车的速度 4.直道模式 5.弯道模式"))
        res = load("ins1.json")
        t1 = MyThread(ser)
        stop_Threads = False
        if flag == 1:
            n = res.get("1").get("目标站点")
            t1.start()
            sendDestination = bytes.fromhex(my_dict[n])
            send(sendDestination)
            stop_Threads = True
            t1.join()
        elif flag == 2:
            SaveList = res["2"]  # 指令列表
            ln = len(SaveList)
            t1.start()
            for i in range(ln):
                send_data = SaveList[i]  # input("输入要发送的数据：")   # 需要发送的串口包
                send_data = bytes.fromhex(send_data)
                send(send_data)
                sleep(15)
            stop_Threads = True
            t1.join()

        #直道下
        elif flag == 4:
            choice = int(input(
                "当前为直道模式，请输入您的选择：1.循环往复 2.站点变速模式"))
            if choice == 1:
                num = res.get("直道").get("loop").get("目标站点")
                tim = res.get("直道").get("loop").get("loopTimes")
                sleeptim = res.get("直道").get("loop").get("sleepTime")
                t = MyThread(ser)
                t1.start()
                for i in range(tim):
                    sendDestination = bytes.fromhex(my_dict[num])
                    send(sendDestination)
                    sleep(sleeptim)  # 41
                    send2 = bytes.fromhex(my_dict[1])  # 发送返回指令
                    send(send2)
                    sleep(sleeptim)  # 41
                stop_Threads = True
                t1.join()
            elif choice == 2:
                deslist = res["直道"]["des"]["站点列表"]
                speedlist = res["直道"]["des"]["速度列表"]
                sleeptim2 = res["直道"]["des"]["sleepTime"]
                t1.start()
                for i in range(len(deslist)):
                    speed = speedlist[i]
                    sendDestination = bytes.fromhex(my_dict[deslist[i]])
                    speed = bytes.fromhex(speedSet(speed))
                    send(speed)
                    sleep(1)
                    send(sendDestination)
                    sleep(17)
                stop_Threads = True
                t1.join()

        elif flag == 3:  # 设置速度
            speed = res.get("3").get("speed")
            speedSend = speedSet(speed)
            speedSend = bytes.fromhex(speedSend)
            t1.start()
            send(speedSend)  # 发送设置速度指令
            print("设置速度成功")
            stop_Threads = True
            t1.join()

        #弯道下
        else:
            choice = int(input(
                "当前为弯道模式，请输入您的选择：1.循环往复 2.站点变速模式"))
            if choice == 1:
                num = res.get("弯道").get("loop").get("目标站点")
                tim = res.get("弯道").get("loop").get("loopTimes")
                sleeptime = res.get("弯道").get("loop").get("sleepTime")
                t = MyThread(ser)
                t1.start()
                for i in range(tim):
                    sendDestination = bytes.fromhex(my_dict[num])
                    send(sendDestination)
                    sleep(sleeptime)  # 41
                    send2 = bytes.fromhex(my_dict[1])  # 发送返回指令
                    send(send2)
                    sleep(sleeptime)  # 41
                stop_Threads = True
                t1.join()
            elif choice == 2:
                deslist = res["弯道"]["des"]["站点列表"]
                speedlist = res["弯道"]["des"]["速度列表"]
                sleeptime2 = res["弯道"]["des"]["sleepTime"]
                t1.start()
                for i in range(len(deslist)):
                    speed = speedlist[i]
                    sendDestination = bytes.fromhex(my_dict[deslist[i]])
                    speed = bytes.fromhex(speedSet(speed))
                    send(speed)
                    sleep(1)
                    send(sendDestination)
                    sleep(sleeptime2)
                stop_Threads = True
                t1.join()

    '''
    while True:


        正反都停：  
        "站点列表": [2,3,4,5,4,3,2,1],
        "速度列表": [2000,4000,4000,2000,2000,4000,4000,2000]
         sleep:17
        只正停：
         "站点列表":[2,3,4,5,1],
         "速度列表": [2000,4000,4000,2000,2000]
         sleep(17)
         只反停：
         "站点列表":[5,4,3,2,1],
         "速度列表": [2000,2000,4000,4000,2000]
         sleep(40)
    '''