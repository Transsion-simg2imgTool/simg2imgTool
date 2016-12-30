#!/usr/bin/env python
#coding:utf-8
# ${product_name} ${osapp_zip_name} ${diff_os_zip}  ${Product_APK_Version}
#         1              2                 3                4                                 
# Product_APK_Version  = ${JENKINSWORKSPACE}/Product_APK_Version  
import os
import sys
import zipfile
import glob
import time
import subprocess
import hashlib

num = 0
bugnum = 0
def set_dev_info():
    global osapp_zip_name
    global out_osapp_zip_dir                          #存放所有集成zip包的目录
    global outsystemimgrepkg_dir                      #image存放目录
    global app_config_version_new
    global app_config_version_old
    global PRODUCTNAME
    global App_config_file_name
    global Product_APK_Version_dir
    global App_config_file
    global app_config
    global file_time
    global appversionzipdir
    global out_readme_dir
    global out_readme_dir_for_app
    global product_Integrationfiledir
    global SCRIPT_PATH
    global Settings_Group_app_readme_file
    global Telephone_Group_app_readme_file
    global Message_Group_app_readme_file
    global Launcher_Group_app_readme_file
    global SystemUI_Group_app_readme_file 
    global release_osapp_zip_dir 
    global out_app_zip_diff_dir
    Settings_Group_app_readme_file = []
    Telephone_Group_app_readme_file = []
    Message_Group_app_readme_file = []
    Launcher_Group_app_readme_file = []
    SystemUI_Group_app_readme_file = []
    new_packagesapp=[]

    PRODUCTNAME=sys.argv[1]
    SCRIPT_PATH = '/work/workspace/jenkins/proj/simg2imgTool/apkversion'           #脚本路径
    appversionzipdir='/work/workspace/jenkins/proj/talpa_apps'                     #获取发布文件路径
    out_readme_dir='/work/OSTeam/simg2img/out_readme_dir'                          #输出文件路径
    out_osapp_zip_dir='/work/OSTeam/simg2img/out_osapp_zip_dir'
    release_osapp_zip_dir='/work/OSTeam/simg2img/talpa_apps_zip_release/'+PRODUCTNAME
    out_app_zip_diff_dir='/work/OSTeam/simg2img/out_osapp_zip_dir_diff/'+PRODUCTNAME
    outsystemimgrepkg_dir='/work/OSTeam/simg2img/out_systemimg/'+PRODUCTNAME
    if not os.path.exists(release_osapp_zip_dir):
        os.system('mkdir -p '+release_osapp_zip_dir)
    if not os.path.exists(out_app_zip_diff_dir):
        os.system('mkdir -p '+out_app_zip_diff_dir)

    app_config_version_new='1.1.1.0'
    app_config_version_old='1.1.1.1'
    osapp_zip_name=sys.argv[2]
    print ('1. osapp_zip_name:'+str(osapp_zip_name))
    osapp_zip_name=str(osapp_zip_name)
    if osapp_zip_name =='None':
        osapp_zip_name=findlastzipfile(out_osapp_zip_dir+'/'+PRODUCTNAME)
    else:
        osapp_zip_name=out_osapp_zip_dir+'/'+PRODUCTNAME+'/'+osapp_zip_name
    print ('2. osapp_zip_name:'+str(osapp_zip_name))
    if os.path.exists(osapp_zip_name):                                           #获取当前集成包的版本号：app_config_version_new
        app_config_version_new=os.path.basename(osapp_zip_name)
        app_config_version_new=str(osapp_zip_name).split('-')[2].replace(' ','')
    print ('app_config_version_new: '+str(app_config_version_new)) 
   
    outsystemimgrepkg_dir = outsystemimgrepkg_dir+'/'+app_config_version_new
    if not os.path.exists(outsystemimgrepkg_dir):
        os.system('mkdir -p '+outsystemimgrepkg_dir)
    App_config_file_name = PRODUCTNAME+'-'+app_config_version_new
    Product_APK_Version_dir = sys.argv[4]
    App_config_file = Product_APK_Version_dir+'/'+App_config_file_name           #本次集成对应版本信息文件的目录
    
    out_readme_dir_for_app = ''
    app_config={}
    app_config=Analytical_os_app_config(App_config_file,'app_config')            #获取发布模块配置信息
    file_time = time.strftime("%Y%m%d%H",time.localtime())                       #获取当前时间 2016122217 格式
    if not os.path.exists(out_readme_dir+'/'+PRODUCTNAME):
        os.system('mkdir -p '+out_readme_dir+'/'+PRODUCTNAME)
    out_readme_dir=str(out_readme_dir+'/'+PRODUCTNAME)
    print ('SCRIPT_PATH:'+str(SCRIPT_PATH))
    print ('Product_name:'+str(PRODUCTNAME))
    print ('app_config_version:'+str(app_config_version_new))
    print ('app_config:'+str(app_config))
    print ('appversionzipdir:'+str(appversionzipdir))
    print ('out_readme_dir:'+str(out_readme_dir))    
        


def getappzip_diff(outdir,tardir):
    full_apps_zip = glob.glob(tardir + '/apps*-*-*.zip')
    print 'full_apps_zip: '+str(full_apps_zip)
    release_app_zip_name=findlastzipfile(tardir)
    new_release_app_zip_name=osapp_zip_name
    zip1=str(new_release_app_zip_name)
    zip2=str(release_app_zip_name)
    if os.path.exists(release_app_zip_name):
        app_config_version_old=os.path.basename(release_app_zip_name)
        app_config_version_old=str(release_app_zip_name).split('-')[2].replace(' ','')
    print ('app_config_version_old: '+str(app_config_version_old)) 
    print 'zip1:'+zip1
    print 'zip2:'+zip2
    foldername1=os.path.basename(zip1).split('.zip')[0]
    foldername2=os.path.basename(zip2).split('.zip')[0]
    print 'foldername1: '+foldername1
    print 'foldername2: '+foldername2
    ex_zip(zip1,tardir+'/',foldername1)
    ex_zip(zip2,tardir+'/',foldername2)
    if not os.path.exists(outdir):
        os.system('sudo mkdir -p ' + outdir)
    os.system('sudo chown -R jenkins:jenkins ' + tardir+'/*')
    apps_diffzip=zipfile.ZipFile(outdir + '/apps-'+'-'+app_config_version_old+'_update_'+app_config_version_new+'.zip','w',zipfile.ZIP_DEFLATED)
    os.chdir(tardir+"/"+foldername1)
    for root, dirs, files in os.walk("."):
        for name in files:
            print(os.path.join(root, name))
            exit = os.path.exists(tardir+"/"+foldername2+"/"+os.path.join(root, name))
            print tardir+"/"+foldername2+os.path.join(root, name)
            print exit
            if exit:
                ofs1=open(tardir+"/"+foldername1+"/"+os.path.join(root, name))
                ofs2=open(tardir+"/"+foldername2+"/"+os.path.join(root, name))
                if getHash(ofs1) != getHash(ofs2):
                    apps_diffzip.write(os.path.join(root, name))
            else:
                apps_diffzip.write(os.path.join(root, name))
    os.system('sudo rm -rf '+tardir+'/'+foldername1)
    os.system('sudo rm -rf '+tardir+'/'+foldername2)

#def ex_zip(zipfile):
#    outzipfilepath=str(os.path.abspath(zipfile)).replace('.zip','')
#    print ('outzipfilepath:'+str(outzipfilepath))
#    os.system('sudo unzip -o -q '+zipfile+' -d '+outzipfilepath)
#    return outzipfilepath    
def ex_zip(f,extract_zip_dir,zipdir):
	os.system('sudo unzip -o -q '+f+' -d '+extract_zip_dir+zipdir)

def getHash(f):
    line=f.readline()
    hash=hashlib.md5()
    while(line):
        hash.update(line)
        line=f.readline()
    return hash.hexdigest()
    
def findlastzipfile(zipdir):
    print ('zipdir:'+str(zipdir))
    files=glob.glob(zipdir + '/*.zip')
    print ('files:'+str(files))
    if files.__len__() < 1:
        print ('zip file is not exists!')
        return False
    fctimes={}
    ctimes=[]
    for file in files:
        fileinfo=os.stat(file)
        time=(fileinfo.st_ctime)
        fctimes[time]=(file)
        ctimes.append(time)
    print (str(fctimes))
    ctimes=max(ctimes)
    print ('max zip file :'+str(fctimes[ctimes])+' time:'+str(ctimes))
    return str(fctimes[ctimes])    


def Analytical_os_app_config(os_app_config_file,pra):
    app_config={} 
    app_config_version_new=''  
    if os.path.exists(os_app_config_file): 
        ozcf=open(os_app_config_file)  
        ozcflines = ozcf.readlines()    
        if ozcflines != None:    
            for row in ozcflines:  
                row = row.strip() 
                if row.split('=')[0].replace(' ','')=='app_config' and pra=='app_config':
                    app_config_name=row.split('=')[1].replace(' ','').replace('\n','').replace('\r','').replace('\t','').replace('{','').replace('}','').replace('\'','').strip()
                    app_config_name=app_config_name.split(',') 
                    if app_config_name !=None:
                        for al in app_config_name:
                            app_config[al.split(':')[0]]=al.split(':')[1]
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
    if PRODUCTNAME !='' and app_config !=None and app_config_version_new !='': 
        if os.path.exists(out_readme_dir) and os.path.exists(appversionzipdir): 
            os.system('sudo mkdir -p ' + out_readme_dir+'/readme-' + PRODUCTNAME+'-'+app_config_version_new+'-'+file_time)
            for apk in app_config:  
                if apk=='product_Integration':
                    continue
                print ('apk_app_config:'+str((str(apk)+'_'+str(app_config[apk])))) 
                if os.path.exists(appversionzipdir+'/'+str(apk)+'/'+str(app_config[apk])+'/'+'Android.mk'):
                    apkname=readAndroidmk(appversionzipdir+'/'+str(apk)+'/'+str(app_config[apk])+'/'+'Android.mk',':=','LOCAL_SRC_FILES').replace('.apk','')
                    if apkname==(str(apk)+'_'+str(app_config[apk])):
                        os.chdir(appversionzipdir)
                        os.system('sudo mkdir -p ' + out_readme_dir+'/readme-' + PRODUCTNAME+'-'+app_config_version_new+'-'+file_time+'/')
                        out_readme_dir_for_app = (out_readme_dir+'/readme-' + PRODUCTNAME+'-'+app_config_version_new+'-'+file_time)
                        print ('out_readme_dir_for_app: '+out_readme_dir_for_app)
                        if os.path.exists(appversionzipdir+'/'+str(apk)+'/'+str(app_config[apk])+'/'+'Readme.txt'):   
                            os.system('sudo cp -raf '+appversionzipdir+'/'+str(apk)+'/'+str(app_config[apk])+'/'+'Readme.txt'+' '+ out_readme_dir+'/readme-' + PRODUCTNAME+'-'+app_config_version_new+'-'+file_time+'/'+'Readme_'+str(apk)+'.txt')
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
            os.system('sudo mkdir -p ' + out_readme_dir+'/readme-' + PRODUCTNAME+'-'+app_config_version_new)
            os.system('sudo cp -raf '+SCRIPT_PATH+'/BugReports.txt'+' '+ out_readme_dir+'/readme-' + PRODUCTNAME+'-'+app_config_version_new+'/'+'BugReports'+'_'+app_config_version_new+'.txt')
            os.system('sudo cp -raf '+SCRIPT_PATH+'/BugReports.txt'+' '+ outsystemimgrepkg_dir+'/'+'BugReports'+'_'+app_config_version_new+'.txt')
            os.system('sudo rm -rf '+out_readme_dir_for_app)
            os.system('sudo rm -rf '+out_readme_dir)

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

if __name__ == '__main__':
    set_dev_info()
    pack_osapp_zip()
    if sys.argv[3]=='1':
        getappzip_diff(out_app_zip_diff_dir,release_osapp_zip_dir)
    