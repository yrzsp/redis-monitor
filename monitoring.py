#-*- coding:utf-8 -*-

import os
import time
import telnetlib
from multiprocessing import Process
from socket import *

def get_ip_status(ip,port):
    """
    作用：扫描端口是否被使用
    返回：True or False
    """
    server = telnetlib.Telnet()
    try:
        server.open(ip,port,timeout=5)
        print("connect is established!")
        server.close()
        return True
    except Exception as err:
        print(err)
        server.close()
        return False

def open_conf(conf_dir):
    try:
        with open(conf_dir,"r") as f:
            conf_dict = {}
            for conf in f.readlines():
                conf_dict[conf.split(" ")[0]] = conf.split(" ")[1].strip("\n")
            return conf_dict
    except Exception as err:
        print(err)

def judge_status(redis_conf):
    try:
        with open(redis_conf,'r') as f:
            for conf in f.readlines():
                if conf.split(" ")[0] == 'slaveof':
                    return False
            return True
    except Exception as err:
        print(err)
        return False

def response_time(ip,monitoring_time):
    resSocket = socket(AF_INET, SOCK_STREAM)
    localAddr = (ip,7788)
    resSocket.bind(localAddr)
    resSocket.listen(2)
    while True:
	print("等待连接**********************")	
	newsocket, newAddr = resSocket.accept()
	print("连接完成，接下来处理数据")
	try:
            time.sleep(2)
	    newsocket.send(monitoring_time)
	finally:
	    newsocket.close()

def request_time(ip,local_time):
    time.sleep(10)
    try:
        cliSocket = socket(AF_INET, SOCK_STREAM)
        cliSocket.connect((ip,7788))
        res_time = cliSocket.recv(1024)
        print(res_time,"******************************")
        if res_time < local_time:
	    return True
        else:
	    return False
    except Exception as err:
	print(err)
    finally:
	cliSocket.close()

if __name__ == '__main__':
    os.system('service redis_master start')
    monitoring_time = str(time.time())
    print(monitoring_time)
    conf_dict = open_conf('/root/pyscript1/monitoring.conf')
    print(conf_dict)
    p = Process(target=response_time,args=(conf_dict['localip'],monitoring_time))
    p.start()
    redis_status = judge_status(conf_dict['redis_conf_dir'])
    if request_time(conf_dict['ip'],monitoring_time) and redis_status:
	try:
	    print('重启的机器变为从服务器')
            with open(conf_dict['redis_conf_dir'],'a') as f:
		conf = "slaveof "+conf_dict['ip']+" 6379"
		f.write(conf)
	    os.system('ps -ef | grep redis')
	    os.system('pkill redis-server')
            time.sleep(5)
	    os.system('service redis_master start')
	    os.system('ps -ef | grep redis')
        except Exception as err:
                print(err)	
    while True:
        redis_status = judge_status(conf_dict['redis_conf_dir'])
	print(redis_status)
	os.system('ps -ef | grep redis')
        if not get_ip_status(conf_dict['ip'], conf_dict['port']) and not redis_status:
            try:
                with open(conf_dict['redis_conf_dir'],'r') as f:
                    confs = f.readlines()
                    #print(confs)
                    for i in range(len(confs)):
                        if confs[i].split(" ")[0] == 'slaveof':
                            confs[i] = ""
                    #print(confs)
                    with open(conf_dict['redis_conf_dir'],'w+') as newf:
                        newf.writelines(confs)
	        os.system('ps -ef | grep redis')
		os.system('pkill redis-server')
                time.sleep(5)
		os.system('service redis_master start')
	        os.system('ps -ef | grep redis')
            except Exception as err:
                print(err)
        time.sleep(2)
