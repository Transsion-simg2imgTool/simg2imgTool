#!/usr/bin/env python
#coding:utf-8

import os
import sys
import zipfile
import glob
import time
import subprocess
import hashlib

num = 0
bugnum = 0
def setevinfo():
    global product_name
    global app_config
    global file_time
    global appversionzipdir
    global out_readme_dir
    global out_readme_dir_for_app
    global product_Integrationfiledir
    global SCRIPT_PATH
    global app_config_version
    global Settings_Group_app_readme_file
    global Telephone_Group_app_readme_file
    global Message_Group_app_readme_file
    global Launcher_Group_app_readme_file
    global SystemUI_Group_app_readme_file 
    global outsystemimgrepkg_dir
    Settings_Group_app_readme_file = []
    Telephone_Group_app_readme_file = []
    Message_Group_app_readme_file = []
    Launcher_Group_app_readme_file = []
    SystemUI_Group_app_readme_file = []

    new_packagesapp=[]
    SCRIPT_PATH = '/work/workspace/jenkins/proj/simg2imgTool/apkversion'           #脚本路径
    appversionzipdir='/work/workspace/jenkins/proj/talpa_apps'                     #获取文件路径
    out_readme_dir='/work/OSTeam/simg2img/out_readme_dir'                          #输出文件路径
    out_readme_dir_for_app = ''
    product_name=Analytical_os_app_config(sys.argv[1],'product_name')              #获取项目名称
    app_config={}
    app_config=Analytical_os_app_config(sys.argv[1],'app_config')                  #获取发布模块配置信息
    app_config_version=''
    app_config_version=Analytical_os_app_config(sys.argv[1],'app_config_version')  #获取本次发布集成版本号
    file_time = time.strftime("%Y%m%d%H",time.localtime())                         #获取当前时间 2016122217 格式
    outsystemimgrepkg_dir='/work/OSTeam/simg2img/out_systemimg/'+product_name+'/'+app_config_version
    if not os.path.exists(out_readme_dir+'/'+product_name):
        os.system('mkdir -p '+out_readme_dir+'/'+product_name)
    if not os.path.exists(outsystemimgrepkg_dir):
        os.system('mkdir -p '+outsystemimgrepkg_dir)
    out_readme_dir=str(out_readme_dir+'/'+product_name)
    print ('SCRIPT_PATH:'+str(SCRIPT_PATH))
    print ('Product_name:'+str(product_name))
    print ('app_config_version:'+str(app_config_version))
    print ('app_config:'+str(app_config))
    print ('appversionzipdir:'+str(appversionzipdir))
    print ('out_readme_dir:'+str(out_readme_dir))
   

def Analytical_os_app_config(os_app_config_file,pra):
    app_config={} 
    app_config_version=''  
    if os.path.exists(os_app_config_file): 
        ozcf=open(os_app_config_file)  
        ozcflines = ozcf.readlines()    
        if ozcflines != None:    
            for row in ozcflines:  
                row = row.strip() 
                if row.split(':')[0].replace(' ','')=='product_name' and pra=='product_name': 
                    product_name = row.split('product_name:')[1].replace(' ','').replace('\n','').replace('\r','').replace('\t','').replace('{','').replace('}','').replace('\'','').strip()
                    if product_name!= None:
                        return product_name
                if row.split('=')[0].replace(' ','')=='app_config' and pra=='app_config':
                    app_config_name=row.split('=')[1].replace(' ','').replace('\n','').replace('\r','').replace('\t','').replace('{','').replace('}','').replace('\'','').strip()
                    app_config_name=app_config_name.split(',') 
                    if app_config_name !=None:
                        for al in app_config_name:
                            app_config[al.split(':')[0]]=al.split(':')[1]
                if row.split(':')[0].replace(' ','')=='app_config_version' and pra=='app_config_version':  
                    app_config_version=row.split(':')[1].replace(' ','').replace('\n','').replace('\r','').replace('\t','').replace('{','').replace('}','').replace('\'','').strip()
                    return app_config_version
        if pra=='app_config' and app_config !=None:
            return app_config

def readAndroidmk(Androidmkpathfile,splitarg,filearg):  
    apkfile_object = open(os.path.join(Androidmkpathfile))  
    for mkline in apkfile_object:   
        if mkline.split(splitarg)[0].replace(' ','')==filearg:   
            strg=''
            strg=mkline.split(splitarg)[1].replace('\n','').replace('\r','').replace('\t','').replace(' ','')  
            return strg

def pack_osapp_zip():
    out_readme_dir_for_app = ''
    if product_name !='' and app_config !=None and app_config_version !='': 
        if os.path.exists(out_readme_dir) and os.path.exists(appversionzipdir): 
            os.system('sudo mkdir -p ' + out_readme_dir+'/readme-' + product_name+'-'+app_config_version+'-'+file_time)
            for apk in app_config:  
                if apk=='product_Integration':
                    continue
                print ('apk_app_config:'+str((str(apk)+'_'+str(app_config[apk])))) 
                if os.path.exists(appversionzipdir+'/'+str(apk)+'/'+str(app_config[apk])+'/'+'Android.mk'):
                    apkname=readAndroidmk(appversionzipdir+'/'+str(apk)+'/'+str(app_config[apk])+'/'+'Android.mk',':=','LOCAL_SRC_FILES').replace('.apk','')
                    if apkname==(str(apk)+'_'+str(app_config[apk])):
                        os.chdir(appversionzipdir)
                        os.system('sudo mkdir -p ' + out_readme_dir+'/readme-' + product_name+'-'+app_config_version+'-'+file_time+'/')
                        out_readme_dir_for_app = (out_readme_dir+'/readme-' + product_name+'-'+app_config_version+'-'+file_time)
                        print ('out_readme_dir_for_app: '+out_readme_dir_for_app)
                        if os.path.exists(appversionzipdir+'/'+str(apk)+'/'+str(app_config[apk])+'/'+'Readme.txt'):   
                            os.system('sudo cp -raf '+appversionzipdir+'/'+str(apk)+'/'+str(app_config[apk])+'/'+'Readme.txt'+' '+ out_readme_dir+'/readme-' + product_name+'-'+app_config_version+'-'+file_time+'/'+'Readme_'+str(apk)+'.txt')
                            readme_files = 'Readme_'+str(apk)+'.txt'
                            print ('readme_file: '+readme_files)
                            #Settings_Group
                            if str(apk) =='settings_sprd6' or str(apk)=='talpacollect' or str(apk)=='OTA' or str(apk)=='talpaConfig' or str(apk)=='talpa_deskclock' or str(apk)=='SetupWizard_sprd' or str(apk)=='settingsProvider_sprd6' or str(apk)=='OS_PluginService':
                                Settings_Group_app_readme_file.append(readme_files)
							#Telephone_Group
                            if str(apk) =='Dialtact' or str(apk)=='ContactsProvider_talpa' or str(apk)=='TelephonyProvider6':
                                Telephone_Group_app_readme_file.append(readme_files)
							#Message_Group
                            if str(apk) =='message' or str(apk)=='Netmanager' or str(apk)=='BatteryManager':
                                Message_Group_app_readme_file.append(readme_files)
							#Launcher_Group
                            if str(apk) =='launcher' or str(apk)=='ChangeWallpaper' or str(apk)=='TalpaTheme':
                                Launcher_Group_app_readme_file.append(readme_files)
							#SystemUI_Group
                            if str(apk) =='SystemUI6':
                                SystemUI_Group_app_readme_file.append(readme_files)
                        #new_packagesapp.append(apk) 
                print ('apk_name: '+str(apk))
                print ('apk_version: '+str(app_config[apk]))
            readme_file(out_readme_dir_for_app)
            os.system('sudo mkdir -p ' + out_readme_dir+'/readme-' + product_name+'-'+app_config_version)
            os.system('sudo cp -raf '+SCRIPT_PATH+'/BugReports.txt'+' '+ out_readme_dir+'/readme-' + product_name+'-'+app_config_version+'/'+'BugReports'+'_'+app_config_version+'.txt')
            os.system('sudo cp -raf '+SCRIPT_PATH+'/BugReports.txt'+' '+ outsystemimgrepkg_dir+'/'+'BugReports'+'_'+app_config_version+'.txt')
            os.system('sudo rm -rf '+out_readme_dir_for_app)

def readme_file(readme_file_path):
    reamdme_file_lines=open(SCRIPT_PATH+'/'+'BugReports.txt','a')
    print (reamdme_file_lines)
    print ('------start write BugReports.txt------')
    reamdme_file_lines.write('\n\n')
    global num 
    global bugnum 
    print ('------start Read Settings Group Readme.txt------')
    reamdme_file_lines.write('＝＝＝＝＝＝＝＝＝＝＝＝Settings Group＝＝＝＝＝＝＝＝＝＝＝＝\n')
    read_group_file(Settings_Group_app_readme_file,num,bugnum,readme_file_path,reamdme_file_lines);
    print ('------end Read Settings Group Readme.txt------\n')
    reamdme_file_lines.write('＝＝＝＝＝＝＝＝＝＝＝＝Settings Group＝＝＝＝＝＝＝＝＝＝＝＝\n\n')

    print ('------start Read Telephone Group Readme.txt------')
    reamdme_file_lines.write('＝＝＝＝＝＝＝＝＝＝＝＝Telephone Group＝＝＝＝＝＝＝＝＝＝＝＝\n')
    read_group_file(Telephone_Group_app_readme_file,num,bugnum,readme_file_path,reamdme_file_lines);
    print ('------end Read Telephone Group Readme.txt------\n')
    reamdme_file_lines.write('＝＝＝＝＝＝＝＝＝＝＝＝Telephone Group＝＝＝＝＝＝＝＝＝＝＝＝\n\n')

    print ('------start Read Message Group Readme.txt------')
    reamdme_file_lines.write('＝＝＝＝＝＝＝＝＝＝＝＝Message Group＝＝＝＝＝＝＝＝＝＝＝＝\n')
    read_group_file(Message_Group_app_readme_file,num,bugnum,readme_file_path,reamdme_file_lines);
    print ('------end Read Message Group Readme.txt------')
    reamdme_file_lines.write('＝＝＝＝＝＝＝＝＝＝＝＝Message Group＝＝＝＝＝＝＝＝＝＝＝＝\n\n')

    print ('------start Read Launcher Group Group Readme.txt------')
    reamdme_file_lines.write('＝＝＝＝＝＝＝＝＝＝＝＝Launcher Group＝＝＝＝＝＝＝＝＝＝＝＝\n')
    read_group_file(Launcher_Group_app_readme_file,num,bugnum,readme_file_path,reamdme_file_lines);
    print ('------end Read Launcher Group Group Readme.txt------\n')
    reamdme_file_lines.write('＝＝＝＝＝＝＝＝＝＝＝＝Launcher Group＝＝＝＝＝＝＝＝＝＝＝＝\n\n')

    print ('------start Read SystemUI Group Group Readme.txt------')
    reamdme_file_lines.write('＝＝＝＝＝＝＝＝＝＝＝＝SystemUI Group＝＝＝＝＝＝＝＝＝＝＝＝\n')
    read_group_file(SystemUI_Group_app_readme_file,num,bugnum,readme_file_path,reamdme_file_lines);
    print ('------end Read SystemUI Group Group Readme.txt------\n')
    reamdme_file_lines.write('＝＝＝＝＝＝＝＝＝＝＝＝SystemUI Group＝＝＝＝＝＝＝＝＝＝＝＝\n\n')

    print ('Readme file count: '+bytes(num))
    print ('Bug list count: '+bytes(bugnum))
    reamdme_file_lines.write('\n'+'App numbers: '+bytes(num)+'\n')
    reamdme_file_lines.write('Bug numbers: '+bytes(bugnum)+'\n')
   
def read_group_file(group_file,file_num,bug_num,read_path,read_file_line):
    global num 
    global bugnum
    if len (group_file)>0:
        for read_file in group_file:
            readme_file = (read_path+'/'+read_file)
            readme_apk_name=read_file.split('_')[1].replace('.txt','')
            #print('Readme_dir: '+readme_file)
            if os.path.exists(readme_file):
                file_num = file_num + 1
                num = file_num
                readme_open = open(readme_file)
                readme_open_lines = readme_open.readlines ()
                if readme_open_lines != None:
                    #print ('readme_open_lines_lens: '+str(len(readme_open_lines)))
                    #print (readme_open_lines)
                    i=0
                    for i,line in enumerate(readme_open_lines):
                        line = line.strip()
                        #line = changecode(line,unicode)
                        #line = line.encode('utf-8')
                        if line.startswith('---'):
                            break
                        i=i+1
                        if i==1:
                            print('    App Name:'+readme_apk_name+'----App Version:'+line) #write
                            read_file_line.write('    App Name:'+readme_apk_name+'————App Version:'+line+' \n')
                            continue
                        if i==2:
                            print ('    '+line)#write
                            #read_file_line.write('    '+line+' \n')
                            continue
                        print ('        '+line)#wirte
                        read_file_line.write('        '+line+' '+' \n')
                    bug_num = bug_num + (i-2)
                    bugnum = bug_num
                    print ('    Log  nums: '+bytes(i-2))#write
        #print ('------end write  %s------\n'%read_file)

    
def changecode (str,encoding):
    if isinstance (str,unicode ):
        return str
    else :
        return unicode (str,encoding )
		
		
if __name__ == '__main__':
    setevinfo()
    pack_osapp_zip()

    
