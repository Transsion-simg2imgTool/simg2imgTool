#!/usr/bin/env python

#   执行脚本命令 ：python ${simg2imgTool}/apkversion/pack_osapp_zip.py ${Product_APK_Version}/${Product_Version}
#	传入值： ${Product_APK_Version}/${Product_Version}——构建输出的配置文件名称
#	Product_APK_Version  ： ${JENKINSWORKSPACE}/Product_APK_Version
#	JENKINSWORKSPACE	： /work/workspace/jenkins/proj
#	Product_Version     构建输出的配置文件名称  包含项目名称：product_name； 配置版本号：app_config_version   ； 模块及版本信息：app_config

#	product_Integrationfile  ： ${JENKINSWORKSPACE}/product_Integration  #中间件文件
#	appversionzipdir   ：  ${JENKINSWORKSPACE}/talpa_apps
import os
import sys
import zipfile
import glob
import time
import subprocess
import hashlib

def setevinfo():
    global product_name
    global app_config
    global file_time
    global appversionzipdir
    global out_osapp_zip_dir
    global PRODUCTNAME
    global product_Integrationfiledir
    global SCRIPT_PATH
    global app_config_version
    global new_packagesapp
    global oscopy_files
    global osincodefile
    new_packagesapp=[]
    oscopy_files=[]
    osincodefile=[]
    SCRIPT_PATH = '/work/workspace/jenkins/proj/simg2imgTool/apkversion'           # 脚本所在目录
    PRODUCTNAME=Analytical_os_app_config(sys.argv[1],'product_name')               # 得到项目名称
    product_Integrationfiledir=os.environ.get('product_Integrationfile')           # 中间件文件所在目录
    appversionzipdir=os.environ.get('appversionzipdir')					           # 发布release软件所在目录	
    out_osapp_zip_dir='/work/OSTeam/simg2img/out_osapp_zip_dir'                    # 输出集成release压缩包所在目录
    app_config={}
    app_config=Analytical_os_app_config(sys.argv[1],'app_config')                  # 字典，存放发布模块名称及其版本号  
    product_name=PRODUCTNAME                                                       # 得到项目名称
    app_config_version=''
    app_config_version=Analytical_os_app_config(sys.argv[1],'app_config_version')  #得到当前配置文件版本号
    file_time = time.strftime("%Y%m%d%H",time.localtime())                         # 得到当前类似：2016122117  格式的时间  
    if not os.path.exists(out_osapp_zip_dir+'/'+PRODUCTNAME):                      # 如果输出发布release集成包所在目录下对应项目的文件夹不存在
        os.system('mkdir -p '+out_osapp_zip_dir+'/'+PRODUCTNAME)                   # 创建一个对应项目的文件夹
    out_osapp_zip_dir=str(out_osapp_zip_dir+'/'+PRODUCTNAME)                       # 重新赋值给out_osapp_zip_dir，输出压缩包文件目录
    print ('SCRIPT_PATH:'+str(SCRIPT_PATH))                                        # 打印出脚本所在目录
    print ('app_config_version:'+str(app_config_version))                          # 打印出当前配置文件版本号
    print ('product_Integrationfiledir:'+str(product_Integrationfiledir))          # 打印出中间件文件所在目录
    print ('out_osapp_zip_dir:'+str(out_osapp_zip_dir))                            # 打印出集成release压缩包所在目录
    print ('app_config:'+str(app_config))                                          # 打印出具体发布模块名称及其版本号  
    print ('appversionzipdir:'+str(appversionzipdir))                              # 打印出所有发布release软件所在目录
def Analytical_os_app_config(os_app_config_file,pra):#对传入的配置文件信息进行处理
    app_config={} #字典 ，存储模块名称及其对应版本号
    app_config_version=''  # 字符  存储构建输出版本号
    if os.path.exists(os_app_config_file):  # 配置文件存在
        ozcf=open(os_app_config_file)  #打开配置文件
        ozcflines = ozcf.readlines()    #读取文件数据
        if ozcflines != None:    #读取数据不为空
            for row in ozcflines:  #遍历读取的字符数据
                row = row.strip() #移除空格符号
                if row.split(':')[0].replace(' ','')=='product_name' and pra=='product_name':  # 分割的第一个字符串为product_name && 传入参数为product_name
                    product_name = row.split('product_name:')[1].replace(' ','').replace('\n','').replace('\r','').replace('\t','').replace('{','').replace('}','').replace('\'','').strip()#分割的第二个参数进行处理后，传递给product_name，
                    if product_name!= None:  #product_name 不为空
                        print ('product_name:'+str(product_name)) #打印出匹配到的product_name字符
                        return product_name
                if row.split('=')[0].replace(' ','')=='app_config' and pra=='app_config': # 分割的第一个字符串为app_config && 传入参数为app_config
                    app_config_name=row.split('=')[1].replace(' ','').replace('\n','').replace('\r','').replace('\t','').replace('{','').replace('}','').replace('\'','').strip()
                    app_config_name=app_config_name.split(',') #再以 ',' 进行分割
                    if app_config_name !=None:
                        for al in app_config_name:
                            app_config[al.split(':')[0]]=al.split(':')[1]
                    print ('app_config_name:'+str(app_config_name))   #mark 
                    print ('app_config:'+str(app_config))
                    print ('app_config:'+str(len(app_config)))
                if row.split(':')[0].replace(' ','')=='app_config_version' and pra=='app_config_version':   # 分割的第一个字符串为app_config_version && 传入参数为app_config_version
                    app_config_version=row.split(':')[1].replace(' ','').replace('\n','').replace('\r','').replace('\t','').replace('{','').replace('}','').replace('\'','').strip()
                    print ('app_config:'+str(len(app_config)))
                    return app_config_version
        if pra=='app_config' and app_config !=None:
            return app_config

def readAndroidmk(Androidmkpathfile,splitarg,filearg):  # 读取Android.mk文件，传入文件名& 分割标志字符 & 字符标志
    apkfile_object = open(os.path.join(Androidmkpathfile))  #读取文件数据
    for mkline in apkfile_object:   #遍历读取的数据
        if mkline.split(splitarg)[0].replace(' ','')==filearg:   #分割的第一个字符串  =  传入的字符
            strg=''
            strg=mkline.split(splitarg)[1].replace('\n','').replace('\r','').replace('\t','').replace(' ','')  # 分割的第二个字符（APK名称）赋值给 strg
            return strg

def pack_osapp_zip():#开始压缩输出release包
    print ('PRODUCTNAME:'+str(PRODUCTNAME))                                     #打印出项目名称
    print ('app_config_version:'+str(app_config_version))                       #打印出集成配置版本号
    print ('product_Integrationfiledir:'+str(product_Integrationfiledir))       #打印出中间件文件所在目录
    print ('out_osapp_zip_dir:'+str(out_osapp_zip_dir))                         #打印出集成release压缩包所在目录
    print ('app_config:'+str(app_config))                                       #打印出具体发布模块名称及其版本号  
    print ('appversionzipdir:'+str(appversionzipdir))                           #打印出所有发布release软件所在目录
    if product_name !='' and app_config !=None and app_config_version !='': #判断三个基本信息不为空
        if os.path.exists(out_osapp_zip_dir) and os.path.exists(appversionzipdir): #判断输出目录 & 获取应用目录不为空
            os.system('sudo mkdir -p ' + out_osapp_zip_dir+'/apps-' + product_name+'-'+app_config_version+'-'+file_time) #创建一个文件夹，暂时存放发布的模块文件
            print ('--------start zip app--------')
            for apk in app_config:   #遍历发布模块配置信息
                print ('apk_app_config:'+str((str(apk)+'_'+str(app_config[apk])))) #打印出当前遍历的 apk 名称&版本号
                print ('Android.mk_exists:'+str(os.path.exists(appversionzipdir+'/'+str(apk)+'/'+str(app_config[apk])+'/'+'Android.mk')))#打印出 判断Android.mk文件是否存在
                if os.path.exists(appversionzipdir+'/'+str(apk)+'/'+str(app_config[apk])+'/'+'Android.mk'):
                    apkname=readAndroidmk(appversionzipdir+'/'+str(apk)+'/'+str(app_config[apk])+'/'+'Android.mk',':=','LOCAL_SRC_FILES').replace('.apk','')#获取APK名称
                    print ('apkname:'+str(apkname))  #打印出apk&版本号名称
                    if apkname==(str(apk)+'_'+str(app_config[apk])): #判断Android.mk中LOCAL_SRC_FILES的值是否与配置文件中的apk信息一致。
                        os.chdir(appversionzipdir)#进入到发布release应用的目录
                        os.system('sudo mkdir -p ' + out_osapp_zip_dir+'/apps-' + product_name+'-'+app_config_version+'-'+file_time+'/'+str(apk)) #在输出目录下创建当前遍历应用的文件夹
                        os.system('sudo cp -raf '+appversionzipdir+'/'+str(apk)+'/'+str(app_config[apk])+'/'+str(apkname)+'.apk'+' '+ out_osapp_zip_dir+'/apps-' + product_name+'-'+app_config_version+'-'+file_time+'/'+str(apk)) #拷贝发布release目录下对应模块文件夹中的APK到当前遍历输出应用文件夹下。
                        os.system('sudo cp -raf '+appversionzipdir+'/'+str(apk)+'/'+str(app_config[apk])+'/'+'Android.mk'+' '+ out_osapp_zip_dir+'/apps-' + product_name+'-'+app_config_version+'-'+file_time+'/'+str(apk))  #拷贝发布release目录下对应模块文件夹中的Android.mk到当前遍历输出应用文件夹下。
                        if os.path.exists(appversionzipdir+'/'+str(apk)+'/'+str(app_config[apk])+'/'+'Readme.txt'):   #如果发布release目录下对应模块文件夹中Readme.txt存在
                            os.system('sudo cp -raf '+appversionzipdir+'/'+str(apk)+'/'+str(app_config[apk])+'/'+'Readme.txt'+' '+ out_osapp_zip_dir+'/apps-' + product_name+'-'+app_config_version+'-'+file_time+'/'+str(apk))#拷贝发布release目录下对应模块文件夹中的Readme.txt到当前遍历输出应用文件夹下。
                        if os.path.exists(appversionzipdir+'/'+str(apk)+'/'+str(app_config[apk])+'/lib'):  #如果发布release目录下对应模块文件夹中lib文件夹存在
                            os.system('sudo cp -raf '+appversionzipdir+'/'+str(apk)+'/'+str(app_config[apk])+'/lib'+' '+ out_osapp_zip_dir+'/apps-' + product_name+'-'+app_config_version+'-'+file_time+'/'+str(apk)) #拷贝发布release目录下对应模块文件夹中的lib文件夹到当前遍历输出应用文件夹下。
                        new_packagesapp.append(apk) #把当前遍历的apk模块名称添加到new_packagesapp列表末尾
                print (str(apk)) #打印出APK名称
                print (str(apk)+':'+str(app_config[apk])) #打印出apk名称&版本号
                if apk=='product_Integration': #如果当前遍历模块名称为product_Integration
                    if os.path.exists(product_Integrationfiledir): #判断中间件文件夹是否存在
                        os.chdir(product_Integrationfiledir)       #存在，进入到该文件夹中
                        os.system('git reset --hard')              #清空当前文件夹下，git仓库与远程不一致的内容 
                        os.system('git clean -fdx')                #清空当前文件夹下，不存在于git仓库中的文件
                        os.system('git pull origin master')        #同步当前文件夹下，git仓库与远程最新一致
                        os.system('git config --global user.email "3033798168@qq.com"')
                        os.system('git config --global user.name "ostest"')
                        os.system('git checkout '+str(app_config[apk]))    #切换到与当前模块版本信息(tag)一致的提交点。
                        if os.path.exists(product_Integrationfiledir+'/'+PRODUCTNAME+'/copy_files'):  #判断当前模块目录下对应项目文件夹中的copy_files文件夹是否存在。
                            os.chdir(product_Integrationfiledir+'/'+PRODUCTNAME+'/copy_files')        #存在，进入该文件夹
                            for dircs,dircnames,codefile in os.walk('.'):  #os.walk('.') 获取当前目录下目录树中的 文件夹路径、文件夹名字、文件名 分别对应 dircs,dircnames,codefile
                                if os.path.exists(dircs):  #判断文件夹路径是否存在
                                    for cf in codefile:    #遍历文件下中的文件
                                        if os.path.isfile(dircs+'/'+cf):  #如果遍历的文件是文件
                                            print ('copy_files:'+str(dircs+'/'+cf))  #打印拷贝的具体文件路径
                                            copy_filescf=str(str(dircs)+'/'+cf).replace('/','',1).replace('.','',1) #将文件具体路径第一个'/'去除，第一个'.'去除;
                                            print ('copy_filescf:'+str(copy_filescf))  #打印拷贝的具体文件
                                            oscopy_files.append(copy_filescf)  #把当前遍历的copy_filescf文件名称添加到oscopy_files列表末尾
                            os.system('sudo mkdir -p ' + out_osapp_zip_dir+'/apps-' + product_name+'-'+app_config_version+'-'+file_time+'/copy_files/')#在输出目录下创建copy_files文件夹
                            os.system('sudo cp -raf '+product_Integrationfiledir+'/'+PRODUCTNAME+'/'+'copy_files/'+' '+ out_osapp_zip_dir+'/apps-' + product_name+'-'+app_config_version+'-'+file_time+'/')#将中间件文件夹下对应项目文件夹中copy_files文件夹，拷贝到输出目录下
                        if os.path.exists(product_Integrationfiledir+'/'+PRODUCTNAME+'/incodefile'): #判断中间件文件夹下对应项目文件夹中是否存在incodefile文件夹
                            osincodefile.append('    vendor/talpa/incodefile/overlay\n') #存在，将'vendor/talpa/incodefile/overlay\n' 字符添加到osincodefile列表末尾
                            os.system('sudo mkdir -p ' + out_osapp_zip_dir+'/apps-' + product_name+'-'+app_config_version+'-'+file_time+'/incodefile/') #在输出目录创建incodefile文件夹
                            os.system('sudo cp -raf '+product_Integrationfiledir+'/'+PRODUCTNAME+'/'+'incodefile/'+' '+ out_osapp_zip_dir+'/apps-' + product_name+'-'+app_config_version+'-'+file_time+'/')#将中间件文件夹下对应项目文件夹中incodefile文件夹，拷贝到输出目录下
                        if os.path.exists(product_Integrationfiledir+'/'+PRODUCTNAME+'/Readme.txt'): #判断中间件文件夹下是否存在Readme.txt文件
                            os.system('sudo mkdir -p ' + out_osapp_zip_dir+'/apps-' + product_name+'-'+app_config_version+'-'+file_time+'/product_Integrationfile') #在输出目录下创建product_Integrationfile文件夹
                            os.system('sudo cp -raf '+product_Integrationfiledir+'/'+PRODUCTNAME+'/Readme.txt'+' '+ out_osapp_zip_dir+'/apps-' + product_name+'-'+app_config_version+'-'+file_time+'/product_Integrationfile')#将中间件文件夹下Readme.txt文件，拷贝到输出目录下的product_Integrationfile文件夹
            talpa_mk_file_make() #写入相关集成模块名称信息到talpa.mk文件
            os.system('sudo cp -raf '+SCRIPT_PATH+'/talpa.mk'+' '+ out_osapp_zip_dir+'/apps-' + product_name+'-'+app_config_version+'-'+file_time+'/')#将新生成的talpa.mk文件复制到输出目录下
            if os.path.exists(SCRIPT_PATH+'/../config/'+PRODUCTNAME+'/readme'): #判断脚本仓库中对应项目下的readme是否存在
                os.system('sudo cp -raf '+SCRIPT_PATH+'/../config/'+PRODUCTNAME+'/readme'+' '+ out_osapp_zip_dir+'/apps-' + product_name+'-'+app_config_version+'-'+file_time+'/')#将脚本所在目录对应项目文件夹下的readme文件拷贝到输出目录下
            zipfolder(out_osapp_zip_dir+'/apps-' + product_name+'-'+app_config_version+'-'+file_time+'/','apps-' + product_name+'-'+app_config_version+'-'+file_time+'.zip') #将输出目录文件夹进行zip压缩
        print(str(('out_osapp_zip:'+out_osapp_zip_dir + '/apps-' + product_name+'-'+app_config_version+'-'+file_time+'.zip'))) #打印出集成发布zip压缩包所在目录
        print('new_packagesapp:'+str(new_packagesapp)+'  oscopy_files:'+str(oscopy_files)+'  osincodefile:'+str(osincodefile)) #打印出本次集成模块及文件名称

def zipfolder(source_dir,output_filename):  #压缩文件夹，传入压缩文件夹目录  及  输出压缩包名称
    osapp_zip = zipfile.ZipFile(out_osapp_zip_dir + '/apps-' + product_name+'-'+app_config_version+'-'+file_time+'.zip','w',zipfile.ZIP_DEFLATED) #创建一个zip文件对象
    pre_len = len(os.path.dirname(source_dir))
    for parent, dirnames, filenames in os.walk(source_dir):
        for filename in filenames:
            pathfile = os.path.join(parent, filename)
            arcname = pathfile[pre_len:].strip(os.path.sep)
            osapp_zip.write(pathfile, arcname)
    osapp_zip.close()
    os.system('sudo rm -rf '+source_dir) #压缩完毕后删除

def getline(the_file_path, line_number):
    if line_number < 1:
        return ''
    for cur_line_number, line in enumerate(open(the_file_path, 'rU')):
        if cur_line_number == line_number-1:
            return line
    return ''

def replacecleanfile():
    for cur_line_number, line in enumerate(open(SCRIPT_PATH+'/'+'talpa.mk', 'rU')):
        if line.split('_')[0].replace(' ','')=='#new' or line.split('_')[0].replace(' ','')=='#copy' or line.split('_')[0].replace(' ','')=='#incode'or line.split('_')[0].replace(' ','')=='#Androidmk':
            replacewritefile(cur_line_number,getline(SCRIPT_PATH+'/'+'talpa.mk',cur_line_number))
            print (str(line))
            print (str(cur_line_number))

def replacewritefile(line,strs):
    f=open(SCRIPT_PATH+'/'+'talpa.mk','r+')
    flist=f.readlines()
    flist[line]=str(str(strs)+'\r')
    f=open(SCRIPT_PATH+'/'+'talpa.mk','w+')
    f.writelines(flist)

def talpa_mk_file_make(): #创建talpa.mk文件
    talpa_mk_file_object_lines=open(SCRIPT_PATH+'/'+'talpa.mk','a')#读取脚本目录下的talpa.mk初始文件
    if len(new_packagesapp)>0:  #apk模块名称列表
        talpa_mk_file_object_lines.write('#new_packages'+'\n'+'PRODUCT_PACKAGES += \\\n')
        print ('---write new_packages for talpa.mk---')
        for na in new_packagesapp:   #遍历写入apk模块名称列表
            talpa_mk_file_object_lines.write('    '+na+' \\\n')
            print ('---write new_packagesadd for talpa.mk---'+str(na))
    if len(oscopy_files)>0:   #copy_filescf文件列表
        talpa_mk_file_object_lines.write('#copy_files'+'\n'+'PRODUCT_COPY_FILES += \\\n')
        print ('---write copy_files for talpa.mk---')
        for cpf in oscopy_files: #遍历写入copy_filescf文件列表
            talpa_mk_file_object_lines.write('    vendor/talpa/copy_files/'+cpf+':'+cpf+' \\\n')
            print ('---write incode_files for talpa.mk---'+str(cpf))
    if len(osincodefile)>0:   #incodefile文件夹
        talpa_mk_file_object_lines.write('#incode_files'+'\n'+'PRODUCT_PACKAGE_OVERLAYS := \\\n')
        print ('---write incodefilesadd for talpa.mk---')
        talpa_mk_file_object_lines.write('    vendor/talpa/incodefile/overlay\n')  #写入incodefile文件所在文件夹
        print ('---write incodefilesadd for talpa.mk---')
    talpa_mk_file_object_lines.write('#Androidmk_end'+'\n')
    print ('---write Androidmk_end for talpa.mk---')
if __name__ == '__main__':
    setevinfo()
    pack_osapp_zip()