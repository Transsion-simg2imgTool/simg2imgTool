#!/usr/bin/env python
#coding:utf-8

# python ${simg2imgTool}/simg2imgTool.py ${product_chip} ${product_name} ${osapp_zip_name} ${ota_package} ${ota_diff_package} ${ANDROID_HOME_dir} ${SIGN_KEY}
#                                              1                 2                3                4             5                     6               7
# product_chip: MTK / SPRC
# product_name: 1513
# osapp_zip_name:  sim2img\out_osapp_zip_dir\目录下各个产品文件夹内\最新的zip包
# ota_package:  0 / 1    是否出ota包:1表示出，0表示不出
# ota_diff_package: 0 / 1     是否出ota差分包:1表示出，0表示不出
# ANDROID_HOME_dir: SPRC_Android7/IDH/idh.code   
# SIGN_KEY: testkey (OTA签名：releasekey;testkey;shared;media)

import os
import sys
import zipfile
import glob
import time
import subprocess
import hashlib

def set_dev_info():
    global PRODUCTNAME
    global SCRIPT_PATH
    global APP_CONFIG_DIR
    global replaced_app
    global date_str
    global date_utc_str
    global file_time
    global appversion
    global productdir
    global outsystemimgrepkg_dir
    global outsystemimgrepkg_dir_new
    global outotatargetrepkg_dir
    global simg2imgtooldir
    global make_ext4fstooldir
    global ota_from_target_filestool
    global mt_ota_from_target_filestool
    global IMG_SIZE
    global SIGN_KEY
    global input_sign_key
    global apkmodules
    global SIGN_KEYTOOL
    global APKSIGN_KEYDIR
    global lib
    global APKSIZE
    global CHIP
    global APKreSIGN
    global out_osapp_zip_dir
    global osapp_zip_name
    global outzipfile
    global ANDROID_out_host_linux
    global ANDROID_ROMCODE
    global ANDROID_HOME_dir
    global PRODUCTotapackage_target_file
    global PRODUCTotapackage_target_file_diff
    replaced_app=[]
    ANDROID_HOME_dir=sys.argv[6]  #源代码具体目录
    ANDROID_ROMCODE='/work/OSTeam/simg2img/ROMCODE' #Android系统源码目录
    ANDROID_HOME_dir=ANDROID_ROMCODE+'/'+ANDROID_HOME_dir #重新赋值，对应项目源码具体目录
    APKSIZE=0L
    osapp_zip_name=sys.argv[3]    #发布的最新的APP集成包
    productdir='/work/OSTeam/simg2img/package_dir' #存放OS 提供的System.img 、 target.zip文件的目录
    lib = 'lib'
    APKreSIGN=True
    apkmodules={}
    input_sign_key = None
    IMG_SIZE=3000000000L
    SCRIPT_PATH = os.getcwd() #当前工作目录->脚本路径
    date_utc_str = subprocess.Popen('date +%s',stdin=subprocess.PIPE,stdout=subprocess.PIPE,shell=True).communicate()[0].rstrip()
    date_str = subprocess.Popen('date',stdin=subprocess.PIPE,stdout=subprocess.PIPE,shell=True).communicate()[0].rstrip() #shell 中执行，创建一个新的管道
    file_time = time.strftime("%Y%m%d%H",time.localtime(time.time())) #获取格式：2016122615 的时间字符。
    SIGN_KEY = 'releasekey'
    if sys.argv[7] =='releasekey' or sys.argv[7] =='testkey' or sys.argv[7] =='shared' or sys.argv[7] =='media': #获取当前使用的签名类型
        SIGN_KEY=sys.argv[7]
    CHIP=sys.argv[1]  #获取当前设置的芯片平台
    PRODUCTNAME=sys.argv[2]   #获取到项目名称
    APP_CONFIG_DIR=SCRIPT_PATH+'/config/'+PRODUCTNAME  #项目配置文件路径
    simg2imgtooldir=SCRIPT_PATH+'/tools/'  #项目工具路径
    outsystemimgrepkg_dir='/work/OSTeam/simg2img/out_systemimg/'+PRODUCTNAME #输出Syetem.img目录
    outotatargetrepkg_dir='/work/OSTeam/simg2img/out_ota/'+PRODUCTNAME       #输出ota目录
    out_osapp_zip_dir='/work/OSTeam/simg2img/out_osapp_zip_dir'              #发布的集成包根目录 
    make_ext4fstooldir=SCRIPT_PATH+'/tools/'                                 #制作ext4文件系统需要使用make_ext4fs命令的工具目录
    PRODUCTotapackage_target_file='/work/OSTeam/simg2img/otapackage_target_file/'+PRODUCTNAME    # 输出的OTA包目录
    PRODUCTotapackage_target_file_diff='/work/OSTeam/simg2img/otapackage_target_file/'+PRODUCTNAME+'_diff' # 输出的OTA——差分包目录
    if not os.path.exists(PRODUCTotapackage_target_file):                    #判断路径存在与否，不存在就创建一个
        os.system('mkdir -p '+PRODUCTotapackage_target_file)
    if not os.path.exists(PRODUCTotapackage_target_file_diff):
        os.system('mkdir -p '+PRODUCTotapackage_target_file_diff)
    print ('CHIP:'+str(CHIP))                                                #打印出芯片平台 :SPRC
    print ('ANDROID_HOME_dir:'+str(ANDROID_HOME_dir))                        #打印出源码路径 :/work/OSTeam/simg2img/ROMCODE/SPRC_Android7/IDH/idh.code
    print ('PRODUCTNAME:'+str(PRODUCTNAME))                                  #打印出项目名称 :1513
    print ('osapp_zip_name:'+str(osapp_zip_name))                            #打印出本次验证的发布集成包的路径 :None
    osapp_zip_name=str(osapp_zip_name)
    if osapp_zip_name =='None':
        osapp_zip_name=findlastzipfile(out_osapp_zip_dir+'/'+PRODUCTNAME)    #如果未指定发布包名称，使用该项目下，最新的集成发布包
    else:
        osapp_zip_name=out_osapp_zip_dir+'/'+PRODUCTNAME+'/'+osapp_zip_name  #获取指定发布包名称
    print ('osapp_zip_name:'+str(osapp_zip_name))                            #打印出本次测试发布包名称 ：/work/OSTeam/simg2img/out_osapp_zip_dir/1513/apps-1513-1.0.***.zip
    appversion='1.1.1.0'
    ANDROID_out_host_linux=ANDROID_HOME_dir+'/out/host/linux-x86/'
    if os.path.exists(osapp_zip_name):
        appversion=os.path.basename(osapp_zip_name)
        appversion=str(osapp_zip_name).split('-')[2].replace(' ','')         #获取本次验证集成包的版本号 
    print ('appversion:'+str(appversion))                                    #打印出版本 :1.0.1612261938
    if not os.path.exists(outsystemimgrepkg_dir):                            #输出目录如果不存在，则创建 system/target
        os.system('mkdir -p '+outsystemimgrepkg_dir)
    outsystemimgrepkg_dir_new = outsystemimgrepkg_dir+'/'+appversion
    if not os.path.exists(outsystemimgrepkg_dir_new):
        os.system('mkdir -p '+outsystemimgrepkg_dir_new)
    if not os.path.exists(outotatargetrepkg_dir):
        os.system('mkdir -p '+outotatargetrepkg_dir)
    SIGN_KEYTOOL=ANDROID_HOME_dir+'/build/target/product/security/'          #签名文件所在目录
    APKSIGN_KEYDIR=SCRIPT_PATH+'/tools/'+CHIP+'/'+'/security'                #app签名文件所在目录
    if not os.path.exists(SCRIPT_PATH+'/tools/'+CHIP+'/'+PRODUCTNAME+'/security/'):  #如果设定的签名目录不存在，就使用默认的
        SIGN_KEYTOOL=SCRIPT_PATH+'/tools/'+CHIP+'/security/'            
        APKSIGN_KEYDIR=SCRIPT_PATH+'/tools/'+CHIP+'/'+'/security'
    else:
        SIGN_KEYTOOL=SCRIPT_PATH+'/tools/'+CHIP+'/'+PRODUCTNAME+'/security/' #如果存在就使用对应项目文件夹下的
        APKSIGN_KEYDIR=SCRIPT_PATH+'/tools/'+CHIP+'/'+PRODUCTNAME+'/security'
    print ('SIGN_KEYTOOL:'+str(SIGN_KEYTOOL))                                #打印出签名工具路径 :/work/workspace/jenkins/proj/simg2imgTool/tools/SPRC/1513/security/  
    print ('APKSIGN_KEYDIR:'+str(APKSIGN_KEYDIR))                            #打印出APK签名文件路径:/work/workspace/jenkins/proj/simg2imgTool/tools/SPRC/1513/security
    mt_ota_from_target_filestool='demo'
    if CHIP==('MTK'):                                                        #MTK平台的OTA脚本所在位置
        mt_ota_from_target_filestool=ANDROID_HOME_dir+'/device/mediatek/build/releasetools/mt_ota_from_target_files' #ota_from_target_files
    os.system('sudo  cp -rf '+SCRIPT_PATH+'/tools/talpa_ota_update '+ANDROID_HOME_dir+'/build/tools/releasetools/talpa_ota_update')
    ota_from_target_filestool=ANDROID_HOME_dir+'/build/tools/releasetools/talpa_ota_update'
    unpack_repack_img()

def get_apps_config():
    if os.path.exists(APP_CONFIG_DIR+'/talpa_apps.config'):#如果脚本目录config下对应的项目中存在talpa_apps.config文件
        cf = open(APP_CONFIG_DIR +"/talpa_apps.config")  #打开该文件
        lines = cf.readlines()
        cf.close
        for row in lines:
            if not row: continue
            row = row.strip()
            value = row.split('=')
            print value
            if 'null' != value[0].strip():
                replaced_app.append(value[0].strip())
    return len(replaced_app)

def findlastzipfile(zipdir): #获取传入目录下最新的文件
    print ('zipdir:'+str(zipdir))      #打印出zip所在目录：/work/OSTeam/simg2img/out_osapp_zip_dir/1513
    files=glob.glob(zipdir + '/*.zip') #获取指定目录下的所有zip格式文件
    print ('files:'+str(files))        #打印出获取的目录下所有的zip文件
    if files.__len__() < 1:
        print ('zip file is not exists!')
        return False
    fctimes={}   #存储文件时间戳-字典
    ctimes=[]
    for file in files:
        fileinfo=os.stat(file)
        time=(fileinfo.st_ctime) #获取文件创建时间
        fctimes[time]=(file)     #以文件-对应修改时间的 方式存放
        ctimes.append(time)
    print (str(fctimes))         #打印出文件按照时间戳添加的字典
    ctimes=max(ctimes)           #获取文件最后修改时间列表中的最大值
    print ('max zip file :'+str(fctimes[ctimes])+' time:'+str(ctimes)) #打印出时间最大值对应的文件，及其时间
    return str(fctimes[ctimes])  #返回对应文件

def delet_nouse_file(dirpath,zip):
    s=os.listdir(dirpath)
    print ('...files '+str(s)) #打印出传入目录下的文件列表
    for zf in s:               #遍历文件列表，删除非需求文件
        if not zf.endswith('.zip') and zip:        
            print ('delet_nouse_file:'+dirpath+'/'+str(zf))
            os.system('sudo rm -rf '+dirpath+'/'+zf)
        else:
            if not zf.endswith('.img') and zip==False:
                print ('delet_nouse_file:'+dirpath+'/'+str(zf))
                os.system('sudo rm -rf '+dirpath+'/'+zf)

def ex_zip(zipfile):
    outzipfilepath=str(os.path.abspath(zipfile)).replace('.zip','')
    print ('outzipfilepath:'+str(outzipfilepath))
    os.system('sudo unzip -o -q '+zipfile+' -d '+outzipfilepath) #解压发布的集成zip包
    return outzipfilepath  #返回解压路径

def readAndroidmk(Androidpath,splitarg,filearg): #读取遍历apk目录下的Android.mk文件，传入文件路径，分割标志字符，分割后的判断标志字符
    apkfile_object = open(os.path.join(Androidpath))
    for mkline in apkfile_object:
        if mkline.split(splitarg)[0].replace(' ','')==filearg:
            strg=''
            strg=mkline.split(splitarg)[1].replace('\n','').replace('\r','').replace('\t','').replace(' ','')
            return strg

def readrmapkAndroidmk(Androidpath,splitarg,filearg): #
    apkfile_object = open(os.path.join(Androidpath))
    for mkline in apkfile_object:
        if mkline.split(splitarg)[0].replace(' ','')==filearg:
            strg=mkline.split(splitarg)[1].replace('\n','').replace('\r','').replace('\t','').strip()
            print (len(strg.split(' ')))
            print (strg.split(' '))
            return strg.split(' ')
    
def replac_app(package_dir,appversionzip): #替换APP 
    apkmodule=[]
    rmapks=[]
    PRODUCT_COPY_FILES=[]
    PROD_COPY=False
    APKSIZE=0L
    if os.path.exists(appversionzip) and appversionzip.endswith('.zip'): #判断传入的发布集成包是否存在，而且是zip格式
        outzipfile=ex_zip(appversionzip)  #返回发布集成包解压后的路径
        if os.path.exists(outzipfile) and os.path.exists(outzipfile+'/talpa.mk'):#判断解压的路径及其目录下的talpa.mk文件是否存在
            if get_apps_config()>0:
                for f in replaced_app:
                    if os.path.exists(package_dir+'/priv-app/'+f):
                        print ('rm:'+str(f))
                        os.system('sudo rm -rf '+package_dir+'/priv-app/'+f)
                    elif os.path.exists(package_dir+'/app/'+f):
                        print ('rm:' + str(f))
                        os.system('sudo rm -rf '+package_dir +'/app/'+f)
            file_object = open(os.path.join(outzipfile,'talpa.mk')) #得到打开talpa.mk文件的具体位置
            print ('file_object:'+str(file_object))
            for line in file_object:
                apk=''
                apk=line.split(' \\')[0].replace('\n','').replace('\r','').replace('\t','').replace(' ','')
                print ('apk:'+str(apk))  #一行一行的显示talpa.mk文件的内容
                apkmodule.append(apk) #装填到apkmodule列表中
            print ('apkmodule:'+str(apkmodule))
            for pline in apkmodule:  #遍历apkmodule
                if 'PRODUCT_COPY_FILES' in pline:
                    PROD_COPY=True
                    print ('PROD_COPY:'+str(PROD_COPY))
                    break
            for pline in apkmodule:
                if 'copy_files' in pline and PROD_COPY and ':' in pline:
                    print ('5556:')
                    PRODUCT_COPY=''
                    PRODUCT_COPY=pline.split(':')[1]
                    PRODUCT_COPY_FILES.append(PRODUCT_COPY)  #将得到的copy-file 装填到对应队列中
            print ('PRODUCT_COPY_FILES:'+str(PRODUCT_COPY_FILES))
            print ('outzipfile:'+str(outzipfile))
            for PRODUCT_COPY_FILE in PRODUCT_COPY_FILES:
                print (str(outzipfile+'/copy_files/'+PRODUCT_COPY_FILE)+':'+str(os.path.exists(outzipfile+'/copy_files/'+PRODUCT_COPY_FILE)))#判断copy_file是否存在
                if os.path.exists(outzipfile+'/copy_files/'+PRODUCT_COPY_FILE):
                    print ('PRODUCT_COPY_FILEdir:'+str(PRODUCT_COPY_FILE).replace('system/','').split('/')[0])
                    PRODUCT_COPY_FILEdir=str(PRODUCT_COPY_FILE).replace('system/','').split('/')[0]
                    if not os.path.exists(package_dir+ PRODUCT_COPY_FILEdir):
                        os.system('sudo mkdir -p '+ package_dir+ PRODUCT_COPY_FILEdir)
                        os.system('sudo chmod 0755 '+ package_dir+ PRODUCT_COPY_FILEdir)  #创建media目录，并修改文件夹权限
                    os.system('sudo cp -rauf ' + outzipfile+'/copy_files/'+PRODUCT_COPY_FILE+'  '+ package_dir+ PRODUCT_COPY_FILEdir) #拷贝copy_file文件到media目录下
                    APKSIZE=getfilesize(outzipfile+'/copy_files/'+PRODUCT_COPY_FILE)+APKSIZE  #获取文件大小，并累计
            for apk in apkmodule:
                if os.path.exists(outzipfile+'/'+apk) and os.path.exists(outzipfile+'/'+apk+'/'+'Android.mk'): #遍历集成包解压目录下的apk模块文件夹及其目录中的Android.mk是否存在
                    print ('apk:'+str(apk)) #打印出当前遍历的模块名称
                    apkm=''
                    apkm=readAndroidmk(outzipfile+'/'+apk+'/'+'Android.mk',':=','LOCAL_MODULE')
                    print ('apkm_LOCAL_MODULE:'+str(apkm)+'  apkm==apk:'+str(apkm==apk)) #打印读取Android.mk文件中的LOCAL_MODULE值，并判断与当前遍历的apk名称是否一致
                    if apkm==apk:  # 如果一致，
                        apk_src_files=''
                        apk_src_files=readAndroidmk(outzipfile+'/'+apk+'/'+'Android.mk',':=','LOCAL_SRC_FILES') #读取LOCAL_SRC_FILES的值-具体的apk名称
                        print ('apkm:'+str(apk)+' apk_src_files:'+str(apk_src_files))
                        if os.path.exists(outzipfile+'/'+apkm+'/'+apk_src_files):#如果对应的apk文件存在
                            if APKreSIGN == True:  #是否重新签名
                                certificate=''
                                certificate=readAndroidmk(outzipfile+'/'+apk+'/'+'Android.mk',':=','LOCAL_CERTIFICATE') #读取apk签名类型LOCAL_CERTIFICATE
                                print ('apkm:'+str(apk)+' certificate:'+str(certificate))
                                cmd = 'sudo java -jar ' + SCRIPT_PATH+'/tools/signapk.jar '+APKSIGN_KEYDIR + '/'+certificate+'.x509.pem '+APKSIGN_KEYDIR + '/'+certificate+'.pk8 '+outzipfile+'/'+apk+'/'+apk_src_files+'  '+outzipfile+'/'+apk+'/'+apkm+'.apk'#签名apk文件指令
                                print ('cmd:'+str(cmd))
                                p = subprocess.Popen(cmd,stdin=subprocess.PIPE,stdout=subprocess.PIPE,shell=True) #执行签名命令
                                if input_sign_key == None:  
                                    key = os.getenv("TALPA_KEY",None) #读取环境变量'TALPA_KEY'。 
                                    if key != None:
                                        p.communicate(key)
                                        p.wait()
                                    else:
                                        p.communicate()
                                else:
                                    p.communicate(input_sign_key)
                                    p.wait()
                            rmapk=[]
                            rmapk=readrmapkAndroidmk(outzipfile+'/'+apk+'/'+'Android.mk',':=','LOCAL_OVERRIDES_PACKAGES') #获取LOCAL_OVERRIDES_PACKAGES的值==需要覆盖原系统apk名称
                            print ('rmapk:'+str(rmapk))
                            if rmapk !=None:
                                for rms in rmapk: #遍历需要覆盖的模块名称
                                    print ('rms:'+str(rms))
                                    if rms != None and os.path.exists(package_dir + '/priv-app/'+rms):
                                        os.system('sudo rm -rf '+package_dir + '/priv-app/'+rms) #移除/priv-app下对应的apk模块
                                    if rms != None and os.path.exists(package_dir + '/app/'+rms):
                                        os.system('sudo rm -rf '+package_dir + '/app/'+rms)      #移除/app下对应的apk模块
                            if os.path.exists(outzipfile+'/'+apk+'/'+apkm+'.apk'):     #如果集成解压包下存在对应apk模块已经签名的apk,          
                                paths=''
                                paths=readAndroidmk(outzipfile+'/'+apk+'/'+'Android.mk',':=','LOCAL_MODULE_PATH')
                                print ('paths:'+str(paths))
                                if "TARGET_OUT_APPS_PRIVILEGED" in paths: #如果TARGET_OUT_APPS_PRIVILEGED存在
                                    if not os.path.exists(package_dir + '/priv-app/'+apk):
                                        os.system('sudo mkdir -p '+package_dir + '/priv-app/'+apk+'/') #如果不存在priv-app/ 就创建一个对应的
                                    else:
                                        os.system('sudo rm -rf '+package_dir + '/priv-app/'+apk)    #否则就删除 ，重新创建一个空的
                                        os.system('sudo mkdir -p '+package_dir + '/priv-app/'+apk+'/')
                                    os.system('sudo chmod 0755 '+package_dir + '/priv-app/'+apk)    #修改文件夹权限
                                    os.system('sudo cp -rauf '+outzipfile+'/'+apk+'/'+apkm+'.apk'+' '+package_dir + '/priv-app/'+apk+'/'+apk+'.apk')#将新的apk模块拷贝进去
                                    APKSIZE=getfilesize(outzipfile+'/'+apk+'/'+apkm+'.apk')+APKSIZE #apk大小累计进APKSIZE
                                    print ('apkmodule:'+str(outzipfile+'/'+apk+'/'+apkm+'.apk'))
                                    if os.path.exists(outzipfile+'/'+apk+'/'+lib):  #判断集成解压包下对应apk模块文件夹下是否存在lib文件夹。
                                        os.system('sudo cp -rauf '+outzipfile+'/'+apk+'/'+lib+' '+package_dir + '/priv-app/'+apk+'/') #如果存在 一并拷贝
                                        os.system('sudo chmod 0755 '+package_dir + '/priv-app/'+apk+'/'+lib)
                                        APKSIZE=getfilesize(outzipfile+'/'+apk+'/'+lib)+APKSIZE  #累计进APKSIZE
                                else:
                                    if not os.path.exists(package_dir + '/app/'+apk): #如果不存在TARGET_OUT_APPS_PRIVILEGED ，同时不存在 对应模块目录
                                        os.system('sudo mkdir -p '+ package_dir + '/app/'+apk+'/') #在app/目录下创建对应模块名称文件夹
                                    else:
                                        os.system('sudo rm -rf '+ package_dir + '/app/'+apk)  #如果已经存在对应模块文件夹，删除，重新创建一个空的
                                        os.system('sudo mkdir -p '+ package_dir + '/app/'+apk+'/')
                                    os.system('sudo chmod 0755 '+package_dir + '/app/'+apk)   #修改文件夹权限
                                    os.system('sudo cp -rauf '+outzipfile+'/'+apk+'/'+apkm+'.apk'+' '+ package_dir + '/app/'+apk+'/'+apkm+'.apk') #拷贝签名的apk到该文件夹下
                                    print ('apkmodule:'+str(outzipfile+'/'+apk+'/'+apkm+'.apk')) #打印出拷贝的文件路径
                                    APKSIZE=getfilesize(outzipfile+'/'+apk+'/'+apkm+'.apk')+APKSIZE #累计大小到APKSIZE
                                    if os.path.exists(outzipfile+'/'+apk+'/'+lib):  #判断集成解压包下对应apk模块文件夹下是否存在lib文件夹。
                                        os.system('sudo cp -rauf '+outzipfile+'/'+apk+'/'+lib+' '+package_dir + '/app/'+apk+'/')  #存有就一并拷贝
                                        os.system('sudo chmod 0755 '+package_dir + '/priv-app/'+apk+'/'+lib)
                                        APKSIZE=getfilesize(outzipfile+'/'+apk+'/'+lib)+APKSIZE  #也累计大小到APKSIZE
                                apkmodules[apkm]=apk_src_files #将所有的apk 装填到apkmodules列表中， 模块名称-对应apk文件名称
        print ('apkmodules:'+str(apkmodules)) #打印出所有APK模块名称&apk文件名称  -字典
        print ('APKSIZE:'+str(APKSIZE))       #打印出添加的模块大小
        if os.path.exists(outzipfile):
            os.system('sudo rm -rf '+outzipfile)  #删除掉解压的集成包
        return APKSIZE
def getfilesize(filenamedir): #传入文件夹路径，获取路径下文件大小
    if os.path.exists(filenamedir):
        if os.path.isdir(filenamedir):#判断是否为目录
            size = 0L
            for root, dirs, files in os.walk(filenamedir):
                size += sum([os.path.getsize(os.path.join(root, name)) for name in files])
            print (str(filenamedir)+' size:'+str(size))
            return size
        if os.path.isfile(filenamedir):#判断是否为文件
            statinfo=os.stat(filenamedir)
            print (str(filenamedir)+' size:'+str(statinfo.st_size))
            return statinfo.st_size

def getpropstring(filename,arg):
    if os.path.exists(filename):
        file_object = open(os.path.join(filename))
        for line in file_object:
            if line.split('=')[0].replace(' ','')==arg:
                prop=line.split('=')[1].replace(' ','').replace('\n','').replace('\r','').replace('\t','')
                print ('prop:'+prop)
                return prop

def unpack_repack_img():  #挂载system.img文件
    img_dir=productdir+'/system_img/'+PRODUCTNAME+'/' #存放system.img底包文件目录
    if not os.path.exists(img_dir):                   #如果底包路径不存在，就创建一个 
        os.system('mkdir -p '+img_dir)
        os.system('sudo chmod 777 '+img_dir)
    print ('unpack '+str(img_dir)+' system.img start...')            #打印出解压包所在目录，
    print ('os.path.exists(img_dir):'+str(os.path.exists(img_dir)))  #打印出解压包所在目录是否存在
    if os.path.exists(img_dir+'/system'):             #如果存在挂载的system文件夹，
        print ('...umount '+str(img_dir)+'system')    #取消挂载，再删除
        os.system('sudo umount '+img_dir+'system')
        os.system('sudo rm -rf '+img_dir+'system')
    delet_nouse_file(img_dir,False)                   #清除非要求文件
    if not os.path.exists(img_dir+'/system.img'):     #如果不存在system.img底包，退出，结束。
        print (str(img_dir)+'system.img is not exists!')
        exit()
    print ('os.path.exists(img_dir+system.img):'+str(os.path.exists(img_dir+'/system.img')))  #打印出是否存在底包
    if not os.path.exists(img_dir+'/system'):         #如果不存在挂载的system文件夹
        os.system('sudo mkdir -p '+img_dir+'/system') #创建挂载需要的system文件夹
    print ('...unpack CHIP: '+str(CHIP)+':'+str(PRODUCTNAME)+' system.img')                  #打印出即将挂载的system.img的芯片信息、项目名称。
    print ('...SCRIPT_PATH:'+str(SCRIPT_PATH))        #打印出脚本路径
    if os.path.exists(SCRIPT_PATH+'/tools/'+CHIP+'/'+PRODUCTNAME+'/simg2img') or os.path.exists(SCRIPT_PATH+'/tools/'+'/simg2img'): #如果脚本路径下，对应项目文件夹存在simg2img工具 或者 tools目录下就存在simg2img工具
        if os.path.exists(SCRIPT_PATH+'/tools/'+CHIP+'/'+PRODUCTNAME+'/simg2img'): #如果对应项目文件下下存在simg2img工具，优先选择他
            simg2imgtooldir=SCRIPT_PATH+'/tools/'+CHIP+'/'+PRODUCTNAME
        else:
            if os.path.exists(SCRIPT_PATH+'/tools/'+CHIP+'/'+'/simg2img'):  #如果对应芯片下存在simg2img工具
                simg2imgtooldir=SCRIPT_PATH+'/tools/'+CHIP
            else:
                simg2imgtooldir=SCRIPT_PATH+'/tools'                       # 以上两个目录均不存在，则选择脚本根目录下的simg2img工具
        print ('...simg2imgtooldir:'+str(simg2imgtooldir))  #打印出 工具所在目录
        os.system('sudo chmod 777 '+simg2imgtooldir+'/simg2img')  #修改simg2img工具权限
        outs=os.system('sudo '+simg2imgtooldir+'/simg2img '+img_dir+'/system.img '+img_dir+'/raw_system') #将sparse image转换为raw image 可以直接 mount挂载
        print ('str(outs):'+str(outs))     #打印出，
        if str(outs)!='0':
            os.system('sudo mount -o loop -t ext4 '+img_dir+'system.img '+img_dir+'system')  #挂载出system.img    raw ext4 image
            print ('Invalid sparse file format at header magi')
        else:
            os.system('sudo mount -o loop -t ext4 '+img_dir+'/raw_system '+img_dir+'system')  # sparse  ext4 image
    else:
        print ('simg2imgtool is not exists!')
        os.system('sudo mount -o loop -t ext4 '+img_dir+'/system.img '+img_dir+'/system')
    os.system('sudo sed -i "s/ro.build.display.id=.*/ro.build.display.id='+PRODUCTNAME+'-'+file_time+'-'+ appversion+'/g" '+img_dir + '/system/build.prop') #sed  将文件/system/build.prop 中第一个匹配的 ro.build.display.id=.* 替换为：ro.build.display.id='+PRODUCTNAME+'-'+file_time+'-'+ appversion+'/g
    os.system('sudo sed -i "s/ro.build.date.utc=[A-Za-z0-9_-.]*/ro.build.date.utc='+date_utc_str+'/g" '+img_dir+'system/build.prop')
    os.system('sudo sed -i "s/ro.build.date=.*/ro.build.date=' + date_str + '/g" '+img_dir+'system/build.prop')
    print ('...unpack CHIP: '+str(CHIP)+':'+str(PRODUCTNAME)+' system.img done')  #解包完成
    APKSIZE=replac_app(img_dir+'system/',osapp_zip_name) #替换解包出来的app，并返回替换入的模块大小
    APKSIZE=getfilesize(osapp_zip_name)  #获取集成zip包的大小
    IMG_SIZE=getfilesize(img_dir+'/system.img')
    if CHIP == 'MTK':
        IMG_SIZE=str(IMG_SIZE)
        IMG_SIZE='2800000000'
    IMG_SIZE=str(IMG_SIZE)
    print ('IMG_SIZE='+str(IMG_SIZE)+' file_time:'+str(file_time)+' APKSIZE:'+str(APKSIZE))
    print ('...repack '+str(CHIP)+':'+str(PRODUCTNAME)+'system.img start...') #开始重新打包system.img
    if os.path.exists(SCRIPT_PATH+'/tools/'+CHIP+'/'+PRODUCTNAME+'/make_ext4fs') or os.path.exists(SCRIPT_PATH+'/tools/'+'/make_ext4fs'): #判断make_ext4fs工具是否存在
        if not os.path.exists(SCRIPT_PATH+'/tools/'+CHIP+'/'+PRODUCTNAME+'/make_ext4fs'): #如果对应tools下对应芯片-项目下不在make_ext4fs
            make_ext4fstooldir=SCRIPT_PATH+'/tools/'   #在tools目录下
        else:
            make_ext4fstooldir=SCRIPT_PATH+'/tools/'+CHIP+'/'+PRODUCTNAME #否则在对应芯片-项目目录下
        os.system('sudo chmod 777 '+make_ext4fstooldir+'/make_ext4fs')  #修改make_ext4fs文件权限
        print ('...make_ext4fs...img ')       #开始重新制作system.img
        os.system('sudo '+make_ext4fstooldir+'/make_ext4fs -T -1 -S ' + SCRIPT_PATH+'/tools/'+CHIP+'/'+PRODUCTNAME + '/file_contexts -l ' + IMG_SIZE + ' -a system '+outsystemimgrepkg_dir_new+'/system-'+PRODUCTNAME+'-'+file_time+'-'+ appversion+'.img '+img_dir+'/system')
    else:
        print ('make_ext4fstool is not exists!') #如果make_ext4fs 工具不存在，则-退出
        exit()
    if os.path.exists(img_dir+'/system'): #制作完成后， 如果挂载的文件夹存在
        print ('...umount '+str(img_dir)+'system...')
        os.system('sudo umount '+ img_dir +'system')  #取消挂载
        os.system('sudo rm -rf '+ img_dir +'system')  #删除挂载文件夹
    if os.path.exists(img_dir+'raw_system'):          #如果 raw_system 文件夹存在
        os.system('sudo rm -rf '+img_dir+'raw_system')#删除 raw_system文件夹 
        print (str(('sudo rm -rf '+img_dir+'system_img/raw_system')))
    print ('...repack '+str(CHIP)+':'+str(PRODUCTNAME)+' system.img done...') #重新打包system.img完成
    print ('...out_system_path:'+str(outsystemimgrepkg_dir_new)+str('/system-'+PRODUCTNAME+'-'+file_time+'-'+ appversion+'.img '))

def extract_repack_otatarget_zip():  #制作OTA包
    otatarget_zipdir=productdir+'/target_zip/'+PRODUCTNAME # 对应项目target包存放位置
    ver_name=appversion                                    # 当前集成包的版本号
    otaoutname=PRODUCTNAME+'-'+file_time+'-'+ ver_name     # 输出OTA包的名称 ：1513-2016122714-1.0.1612261938
    if not os.path.exists(otatarget_zipdir):               # 如果存放target包的目录不存在
        os.system('sudo mkdir -p '+otatarget_zipdir)       # 创建对应项目存放target包文件夹
        os.system('sudo chmod 777 '+otatarget_zipdir)
    os.system('rm -rf '+'/tmp/tmp*')                       # 删除之前操作缓存的文件夹
    os.system('rm -rf '+'/tmp/targetfile*')
    os.system('rm -rf '+'/tmp/imgdiff*')
    if os.path.exists(otatarget_zipdir+'/target'):         # 判断target包存放目录下是否存在 target文件夹
        os.system('sudo rm -rf '+otatarget_zipdir+'target')# 存在就先删除
    delet_nouse_file(otatarget_zipdir,True)                # 删除target存放目录下，非需要格式文件
    files=glob.glob(otatarget_zipdir + '/*.zip')           # 匹配文件目录下所有的zip格式的文件
    if files.__len__() < 1:                                # 如果目录下不存在zip文件
        print ('ota target.zip is not exists!')
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
    print ('max ota target.zip file :'+str(fctimes[ctimes])+' time:'+str(ctimes)) #最后修改时间 最靠前的文件
    if os.path.exists(str(fctimes[ctimes])):  #如果文件最后修改时间最新的文件存在
        os.system('sudo chown -R jenkins:jenkins '+otatarget_zipdir)  #由于target包外部可以存放进去，操作前，先修改文件-分组 
        os.system('mkdir -p '+otatarget_zipdir+'/target')             #创建target文件夹
        os.system('unzip -o -q '+str(fctimes[ctimes])+' -d '+otatarget_zipdir+'/target') #解压对应文件到target文件夹下
        print (str('unzip -o -q '+str(fctimes[ctimes])+' -d '+otatarget_zipdir+'/target'))
    os.system('sed -i "s/ro.build.display.id=.*/ro.build.display.id='+PRODUCTNAME+'-'+file_time+'-'+ appversion+'/g" '+otatarget_zipdir + '/target/SYSTEM/build.prop')
    os.system('sed -i "s/ro.build.date.utc=[A-Za-z0-9_-.]*/ro.build.date.utc='+date_utc_str+'/g" '+otatarget_zipdir + '/target/SYSTEM/build.prop')
    os.system('sed -i "s/ro.build.date=.*/ro.build.date='+date_str+'/g" '+otatarget_zipdir + '/target/SYSTEM/build.prop')
    replac_app(otatarget_zipdir+'/target/SYSTEM/',osapp_zip_name) #替换发布的集成包的app
    os.system('sudo chown -R jenkins:jenkins '+otatarget_zipdir)  #修改target存放目录所属用户组
    print ('start make ota package')        #开始重新制作OTA包
    os.chdir(otatarget_zipdir+'/target')    #切换工作目录到 target文件夹下。
    cmd='zip -r -y '+outotatargetrepkg_dir+'/'+'tmp.zip '+'./'  #执行的压缩zip命令
    print ('cmd:'+str(cmd))
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True) #通过管道执行cmd
    outs=p.communicate()
    #print('outs:'+str(outs))
    print ('start make ota tmp.zip')
    os.system('mv '+outotatargetrepkg_dir+'/'+'tmp.zip '+PRODUCTotapackage_target_file+'/'+otaoutname+'_update.zip') #复制压缩的target zip包到输出目录下，并重命名
    os.system('sudo chmod 777 '+ota_from_target_filestool)
    os.chdir(ANDROID_HOME_dir) #进入到源码目录
    if CHIP==('MTK'):
        cmd = ota_from_target_filestool + ' -v -p '+ANDROID_out_host_linux+' -k '+SIGN_KEYTOOL+SIGN_KEY+' -s '+mt_ota_from_target_filestool+' '+PRODUCTotapackage_target_file+'/'+otaoutname+'_update.zip '+outotatargetrepkg_dir+'/'+otaoutname +'.zip'
    else:
        cmd = ota_from_target_filestool + ' -v -p '+ANDROID_out_host_linux+' -k '+SIGN_KEYTOOL+SIGN_KEY+' '+PRODUCTotapackage_target_file+'/'+otaoutname+'_update.zip '+outotatargetrepkg_dir+'/'+otaoutname +'.zip'
    print ('cmd:'+str(cmd))
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
    if input_sign_key != None:
        p.communicate(input_sign_key)
        p.wait()
    else:
        outs=p.communicate()
        #print('outs:'+str(outs))
    print ('stop make ota package...succeed')
    print ('......remove tmp file......')
    os.system('sudo rm -rf '+outotatargetrepkg_dir+'/tmp.zip')
    os.system('sudo rm -rf '+otatarget_zipdir+'/target')
    os.system('rm -rf '+'/tmp/tmp*')
    os.system('rm -rf '+'/tmp/targetfile*')
    os.system('rm -rf '+'/tmp/imgdiff*')
    print ('out_ota_path:'+str(outotatargetrepkg_dir+'/'+otaoutname+'.zip'))

def make_ota_diff(): #制作OTA差分包
    if not os.path.exists(PRODUCTotapackage_target_file):
        print ('PRODUCTotapackage_target_file:'+str(PRODUCTotapackage_target_file)+' not exists!!!')
        exit()
    print ('PRODUCTotapackage_target_file:'+str(PRODUCTotapackage_target_file))
    full_file =os.listdir(PRODUCTotapackage_target_file)
    all_updateota = []
    print ('full_file:'+str(full_file))
    if full_file.__len__() < 1:
        print ('ota target_update.zip is not exists!')
        exit()
    else:
        for f in full_file:
            if f.endswith('_update.zip'):
                all_updateota.append(f)
    if len(all_updateota) <= 1:
        print ('ota target_update.zip is not exists!')
        exit()
    print ('>>>len %d'%(len(all_updateota)))
    max_diff_count = 5
    need_diff_file = []
    last_file = []
    for f in all_updateota:
        fpath = PRODUCTotapackage_target_file + '/' + f
        time = os.path.getctime(fpath)
        if len(need_diff_file) < max_diff_count:
            need_diff_file.append([fpath,time])
        else:
            for nf in need_diff_file:
                if time > nf[1]:
                    need_diff_file.remove(nf)
                    need_diff_file.append([fpath,time])
                    break
        if len(last_file) == 0 or last_file[1] < time:
            last_file = [fpath,time]
    need_diff_file.remove(last_file)
    os.chdir(ANDROID_HOME_dir)
    os.system('pwd')
    for i in xrange(0,len(need_diff_file)):
        to_diff(last_file[0],need_diff_file[i][0],PRODUCTotapackage_target_file_diff)

def to_diff(file1,file2,PRODUCTotapackage_target_file_diff):
    #time1 = os.path.basename(file1).split('-')[1]
    time2 = str(os.path.basename(file2).split('-')[1])+'-'+str(os.path.basename(file2).split('-')[2].replace('_update.zip',''))
    os.system('sudo chmod 777 ' + ota_from_target_filestool)
    if CHIP==('MTK'):
        cmd = ota_from_target_filestool + ' -k '+SIGN_KEYTOOL+SIGN_KEY+' -s '+mt_ota_from_target_filestool+' -i ' + file2 + ' ' + file1 + ' ' + PRODUCTotapackage_target_file_diff + '/' + os.path.basename(file1)[:-4] + '_' + time2 + '.zip'
    else:
        cmd = ota_from_target_filestool + ' -k '+SIGN_KEYTOOL+SIGN_KEY+' -i ' + file2 + ' ' + file1 + ' ' + PRODUCTotapackage_target_file_diff + '/' + os.path.basename(file1)[:-4] + '_' + time2 + '.zip'
    print ('cmd:'+str(cmd))
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
    if input_sign_key != None:
        p.communicate(input_sign_key)
        p.wait()
    else:
        p.communicate()

if __name__ == '__main__':
    set_dev_info()
    if sys.argv[4]=='1':
        extract_repack_otatarget_zip() #制作OTA包
    if sys.argv[5]=='1':
        make_ota_diff()                #制作OTA差分包