# -*- coding: utf-8 -*-
import os
import subprocess
import platform


class auto_adb():
    def __init__(self):
        try:
            with open('adb_directory', "r", encoding='utf-8') as f1:
                adb_directory = f1.read()#读取 adb_directoty 内容并赋值
            adb_path = adb_directory + 'adb.exe'
            print(adb_path)
            subprocess.Popen([adb_path], stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)#创建adb 进程
            self.adb_path = adb_path
        except OSError:
            if platform.system() == 'Windows':#识别操作系统
                adb_path = os.path.join('Tools', 'adb.exe')
                print(adb_path)
                try:
                    subprocess.Popen(
                        [adb_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)# stdout=subprocess.PIPE  输出到 一个文件  stderr=subprocess.PIPE 错误信息输出到一个文件
                    self.adb_path = adb_path
                except OSError:
                    pass
            else:
                try:
                    subprocess.Popen(
                        [adb_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                except OSError:
                    pass
            print('请安装 ADB 及驱动并配置环境变量')
            print('具体链接: https://github.com/wangshub/wechat_jump_game/wiki')
            exit(1)

    def get_screen(self):
        process = os.popen(self.adb_path + ' shell wm size')#不明白
        output = process.read()
        return output

    def run(self, raw_command):
        command = '{} {}'.format(self.adb_path, raw_command)#不明白
        process = os.popen(command)
        output = process.read()
        return output

    def test_device(self):
        print('检查设备是否连接...')
        command_list = [self.adb_path, 'devices']
        process = subprocess.Popen(command_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = process.communicate()#发送和读取process进程数据
        if output[0].decode('utf8') == 'List of devices attached\n\n':
            print('未找到设备')
            print('adb 输出:')
            for each in output:
                print(each.decode('utf8'))
            exit(1)
        print('设备已连接')
        print('adb 输出:')
        for each in output:
            print(each.decode('utf8'))

    def test_density(self):
        process = os.popen(self.adb_path + ' shell wm density')
        output = process.read()
        return output

    def test_device_detail(self):
        process = os.popen(self.adb_path + ' shell getprop ro.product.device')
        output = process.read()
        return output

    def test_device_os(self):
        process = os.popen(self.adb_path + ' shell getprop ro.build.version.release')
        output = process.read()
        return output

    def adb_path(self):
        return self.adb_path
