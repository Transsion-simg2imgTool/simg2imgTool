#!/usr/bin/env python
#coding:utf-8

'''
#执行脚本：
    Name=${product_name}"-"${Versions}
    echo "app_choice:"${app_choice}
    echo "productVersion:"$Name
    if [ ! -f ${Product_APK_Version}/${product_name}"-"${Versions} ]; then #文件不存在
        python ${simg2imgTool}/apkversion/app_VersionConfig.py ${Product_APK_Version} ${product_name} ${Versions} ${app_choice}
    else
        echo "product:"${product_name}" Introduced Failed"
        exit 1
    fi
# 具体参数：
    product_name = 1513
    Versions = 1.0.1612291002
    app_choice = 本次集成所有模块
    productVersion =  product_name-Versions （1513-1.0.1612291002）
    Product_APK_Version = /work/workspace/jenkins/proj/Product_APK_Version/
'''

import os
import sys
import zipfile
import glob
import time
import subprocess
import hashlib

def set_dev_info(): #获取基本信息
    global product_name
    product_name=sys.argv[2]  #得到项目名称
    global Versions
    Versions=sys.argv[3]      #得到集成版本号
    global product_Integrationfile
    product_Integrationfile=sys.argv[1] #输出版本配置文件路径

def  resolveProductVersionfile(app_choice):
    apps=[]
    os_app_config={}
    if app_choice !=None:
        apps=app_choice.split(',')
    print ('app_choice:'+str(app_choice)) #打印出 传入的 app_choice 
    if apps !=None:
        for apk in apps:
            apkversion=os.environ.get(apk) #获取APK版本号 #os.environ.get()得到某环境变量的值。
            if apkversion !=None:
                print ('apk:'+str(apk)+' apkversion:'+str(apkversion)) #打印出遍历的模块名称&版本号
                os_app_config[apk]=apkversion  #存入字典中
    if product_name !=None: #如果项目名称存在
        if os.path.exists(product_Integrationfile+'/'):#版本配置文件输出目录是否存在
            os.system('echo product_name:'+product_name+'>> '+product_Integrationfile+'/'+'/'+product_name+'-'+Versions) #存在-写入：product_name:1513
            if Versions !=None:#集成配置版本号存在
                os.system('echo app_config_version:'+Versions+'>> '+product_Integrationfile+'/'+'/'+product_name+'-'+Versions)#写入app_config_version:1.0.1612291002
            if os_app_config !=None:#存放app模块的字典不为空
                os.system('echo app_config='+str(os_app_config)+'>> '+product_Integrationfile+'/'+'/'+product_name+'-'+Versions)#写入app_config字典内容
            os.chdir(product_Integrationfile+'/')#进入到集成版本配置文件输出目录
            os.system('git config --global user.email "3033798168@qq.com"')
            os.system('git config --global user.name "ostest"')
            os.system('git add '+product_name+'-'+Versions)
            os.system('git commit -sm "Creat-New-productVersion"')
            os.system('git push origin master')
    print ('os_app_config:'+str(os_app_config))

if __name__ == '__main__':
    set_dev_info()
    resolveProductVersionfile(sys.argv[4])