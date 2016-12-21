#!/usr/bin/env python
import os
import sys
import zipfile
import glob
import time
import subprocess
import hashlib

def set_dev_info():
    global product_name
    product_name=sys.argv[2]
    global Versions
    Versions=sys.argv[3]
    global product_Integrationfile
    product_Integrationfile=sys.argv[1]

def  resolveProductVersionfile(app_choice):
    apps=[]
    os_app_config={}
    if app_choice !=None:
        apps=app_choice.split(',')
    print ('app_choice:'+str(app_choice))
    if apps !=None:
        for apk in apps:
            apkversion=os.environ.get(apk)
            if apkversion !=None:
                print ('apk:'+str(apk)+' apkversion:'+str(apkversion))
                os_app_config[apk]=apkversion
    if product_name !=None:
        if os.path.exists(product_Integrationfile+'/'):
            os.system('echo product_name:'+product_name+'>> '+product_Integrationfile+'/'+'/'+product_name+'-'+Versions)
            if Versions !=None:
                os.system('echo app_config_version:'+Versions+'>> '+product_Integrationfile+'/'+'/'+product_name+'-'+Versions)
            if os_app_config !=None:
                os.system('echo app_config='+str(os_app_config)+'>> '+product_Integrationfile+'/'+'/'+product_name+'-'+Versions)
            os.chdir(product_Integrationfile+'/')
            os.system('git config --global user.email "3033798168@qq.com"')
            os.system('git config --global user.name "ostest"')
            os.system('git add '+product_name+'-'+Versions)
            os.system('git commit -sm "Creat-New-productVersion"')
            os.system('git push origin master')
    print ('os_app_config:'+str(os_app_config))

if __name__ == '__main__':
    set_dev_info()
    resolveProductVersionfile(sys.argv[4])