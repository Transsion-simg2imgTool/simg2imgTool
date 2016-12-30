#!/usr/bin/env python

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
    SCRIPT_PATH = '/work/workspace/jenkins/proj/simg2imgTool/apkversion'          
    PRODUCTNAME=Analytical_os_app_config(sys.argv[1],'product_name')               
    product_Integrationfiledir=os.environ.get('product_Integrationfile')          
    appversionzipdir=os.environ.get('appversionzipdir')					          
    out_osapp_zip_dir='/work/OSTeam/simg2img/out_osapp_zip_dir'                    
    app_config={}
    app_config=Analytical_os_app_config(sys.argv[1],'app_config')                  
    product_name=PRODUCTNAME                                                       
    app_config_version=''
    app_config_version=Analytical_os_app_config(sys.argv[1],'app_config_version')  
    file_time = time.strftime("%Y%m%d%H",time.localtime())                        
    if not os.path.exists(out_osapp_zip_dir+'/'+PRODUCTNAME):                      
        os.system('mkdir -p '+out_osapp_zip_dir+'/'+PRODUCTNAME)                  
    out_osapp_zip_dir=str(out_osapp_zip_dir+'/'+PRODUCTNAME)                      
    print ('SCRIPT_PATH:'+str(SCRIPT_PATH))                                       
    print ('Product_name:'+str(product_name))
    print ('app_config:'+str(app_config))                                         
    print ('app_config_version:'+str(app_config_version))                         
    print ('product_Integrationfiledir:'+str(product_Integrationfiledir))          
    print ('appversionzipdir:'+str(appversionzipdir))                              
    print ('out_osapp_zip_dir:'+str(out_osapp_zip_dir))                            
   

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
                        #print ('product_name:'+str(product_name))
                        return product_name
                if row.split('=')[0].replace(' ','')=='app_config' and pra=='app_config':
                    app_config_name=row.split('=')[1].replace(' ','').replace('\n','').replace('\r','').replace('\t','').replace('{','').replace('}','').replace('\'','').strip()
                    app_config_name=app_config_name.split(',') 
                    if app_config_name !=None:
                        for al in app_config_name:
                            app_config[al.split(':')[0]]=al.split(':')[1]
                    #print ('app_config_name:'+str(app_config_name))  
                    #print ('app_config:'+str(app_config))
                    #print ('app_config_len:'+str(len(app_config)))
                if row.split(':')[0].replace(' ','')=='app_config_version' and pra=='app_config_version':  
                    app_config_version=row.split(':')[1].replace(' ','').replace('\n','').replace('\r','').replace('\t','').replace('{','').replace('}','').replace('\'','').strip()
                    #print ('app_config_version:'+str(app_config_version))
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
   # print ('PRODUCTNAME:'+str(PRODUCTNAME))                                    
   # print ('app_config_version:'+str(app_config_version))                      
   # print ('product_Integrationfiledir:'+str(product_Integrationfiledir))      
   # print ('out_osapp_zip_dir:'+str(out_osapp_zip_dir))                        
   # print ('app_config:'+str(app_config))                                       
   # print ('appversionzipdir:'+str(appversionzipdir))                           
    if product_name !='' and app_config !=None and app_config_version !='': 
        if os.path.exists(out_osapp_zip_dir) and os.path.exists(appversionzipdir): 
            os.system('sudo mkdir -p ' + out_osapp_zip_dir+'/apps-' + product_name+'-'+app_config_version+'-'+file_time) 
            print ('-----------start zip app-----------')
            for apk in app_config:  
                print ('apk_app_config:'+str((str(apk)+'_'+str(app_config[apk])))) 
                print ('Android.mk_exists:'+str(os.path.exists(appversionzipdir+'/'+str(apk)+'/'+str(app_config[apk])+'/'+'Android.mk')))
                if os.path.exists(appversionzipdir+'/'+str(apk)+'/'+str(app_config[apk])+'/'+'Android.mk'):
                    apkname=readAndroidmk(appversionzipdir+'/'+str(apk)+'/'+str(app_config[apk])+'/'+'Android.mk',':=','LOCAL_SRC_FILES').replace('.apk','')
                    print ('apkname:'+str(apkname))  
                    if apkname==(str(apk)+'_'+str(app_config[apk])):
                        os.chdir(appversionzipdir)
                        os.system('sudo mkdir -p ' + out_osapp_zip_dir+'/apps-' + product_name+'-'+app_config_version+'-'+file_time+'/'+str(apk)) 
                        os.system('sudo cp -raf '+appversionzipdir+'/'+str(apk)+'/'+str(app_config[apk])+'/'+str(apkname)+'.apk'+' '+ out_osapp_zip_dir+'/apps-' + product_name+'-'+app_config_version+'-'+file_time+'/'+str(apk)) 
                        os.system('sudo cp -raf '+appversionzipdir+'/'+str(apk)+'/'+str(app_config[apk])+'/'+'Android.mk'+' '+ out_osapp_zip_dir+'/apps-' + product_name+'-'+app_config_version+'-'+file_time+'/'+str(apk))  
                        if os.path.exists(appversionzipdir+'/'+str(apk)+'/'+str(app_config[apk])+'/'+'Readme.txt'):   
                            os.system('sudo cp -raf '+appversionzipdir+'/'+str(apk)+'/'+str(app_config[apk])+'/'+'Readme.txt'+' '+ out_osapp_zip_dir+'/apps-' + product_name+'-'+app_config_version+'-'+file_time+'/'+str(apk))
                        if os.path.exists(appversionzipdir+'/'+str(apk)+'/'+str(app_config[apk])+'/lib'):  
                            os.system('sudo cp -raf '+appversionzipdir+'/'+str(apk)+'/'+str(app_config[apk])+'/lib'+' '+ out_osapp_zip_dir+'/apps-' + product_name+'-'+app_config_version+'-'+file_time+'/'+str(apk)) 
                        new_packagesapp.append(apk) 
                print (str(apk)) 
                print (str(apk)+':'+str(app_config[apk])) 
                if apk=='product_Integration': 
                    if os.path.exists(product_Integrationfiledir): 
                        os.chdir(product_Integrationfiledir)       
                        os.system('git reset --hard')              
                        os.system('git clean -fdx')                
                        os.system('git pull origin master')        
                        os.system('git config --global user.email "3033798168@qq.com"')
                        os.system('git config --global user.name "ostest"')
                        os.system('git checkout '+str(app_config[apk]))   
                        if os.path.exists(product_Integrationfiledir+'/'+PRODUCTNAME+'/copy_files'): 
                            os.chdir(product_Integrationfiledir+'/'+PRODUCTNAME+'/copy_files')       
                            for dircs,dircnames,codefile in os.walk('.'):  
                                if os.path.exists(dircs): 
                                    for cf in codefile:    
                                        if os.path.isfile(dircs+'/'+cf):  
                                            print ('copy_files:'+str(dircs+'/'+cf))  
                                            copy_filescf=str(str(dircs)+'/'+cf).replace('/','',1).replace('.','',1) 
                                            print ('copy_filescf:'+str(copy_filescf))  
                                            oscopy_files.append(copy_filescf)  
                            os.system('sudo mkdir -p ' + out_osapp_zip_dir+'/apps-' + product_name+'-'+app_config_version+'-'+file_time+'/copy_files/')
                            os.system('sudo cp -raf '+product_Integrationfiledir+'/'+PRODUCTNAME+'/'+'copy_files/'+' '+ out_osapp_zip_dir+'/apps-' + product_name+'-'+app_config_version+'-'+file_time+'/')
                        if os.path.exists(product_Integrationfiledir+'/'+PRODUCTNAME+'/incodefile'): 
                            osincodefile.append('    vendor/talpa/incodefile/overlay\n') 
                            os.system('sudo mkdir -p ' + out_osapp_zip_dir+'/apps-' + product_name+'-'+app_config_version+'-'+file_time+'/incodefile/') 
                            os.system('sudo cp -raf '+product_Integrationfiledir+'/'+PRODUCTNAME+'/'+'incodefile/'+' '+ out_osapp_zip_dir+'/apps-' + product_name+'-'+app_config_version+'-'+file_time+'/')
                        if os.path.exists(product_Integrationfiledir+'/'+PRODUCTNAME+'/Readme.txt'):
                            os.system('sudo mkdir -p ' + out_osapp_zip_dir+'/apps-' + product_name+'-'+app_config_version+'-'+file_time+'/product_Integrationfile') 
                            os.system('sudo cp -raf '+product_Integrationfiledir+'/'+PRODUCTNAME+'/Readme.txt'+' '+ out_osapp_zip_dir+'/apps-' + product_name+'-'+app_config_version+'-'+file_time+'/product_Integrationfile')
            talpa_mk_file_make()
            os.system('sudo cp -raf '+SCRIPT_PATH+'/talpa.mk'+' '+ out_osapp_zip_dir+'/apps-' + product_name+'-'+app_config_version+'-'+file_time+'/')
            if os.path.exists(SCRIPT_PATH+'/../config/'+PRODUCTNAME+'/readme'): 
                os.system('sudo cp -raf '+SCRIPT_PATH+'/../config/'+PRODUCTNAME+'/readme'+' '+ out_osapp_zip_dir+'/apps-' + product_name+'-'+app_config_version+'-'+file_time+'/')
            zipfolder(out_osapp_zip_dir+'/apps-' + product_name+'-'+app_config_version+'-'+file_time+'/','apps-' + product_name+'-'+app_config_version+'-'+file_time+'.zip')
        print(str(('out_osapp_zip:'+out_osapp_zip_dir + '/apps-' + product_name+'-'+app_config_version+'-'+file_time+'.zip')))
        print ('-----------end  zip app-----------')
        print('  new_packagesapp:'+str(new_packagesapp)+'\n  oscopy_files:'+str(oscopy_files)+'\n  osincodefile:'+str(osincodefile)) 

def zipfolder(source_dir,output_filename):  
    osapp_zip = zipfile.ZipFile(out_osapp_zip_dir + '/apps-' + product_name+'-'+app_config_version+'-'+file_time+'.zip','w',zipfile.ZIP_DEFLATED)
    pre_len = len(os.path.dirname(source_dir))
    for parent, dirnames, filenames in os.walk(source_dir):
        for filename in filenames:
            pathfile = os.path.join(parent, filename)
            arcname = pathfile[pre_len:].strip(os.path.sep)
            osapp_zip.write(pathfile, arcname)
    osapp_zip.close()
    os.system('sudo rm -rf '+source_dir)
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

def talpa_mk_file_make(): 
    talpa_mk_file_object_lines=open(SCRIPT_PATH+'/'+'talpa.mk','a')
    print ('------start write  talpa.mk------')
    if len(new_packagesapp)>0: 
        talpa_mk_file_object_lines.write('#new_packages'+'\n'+'PRODUCT_PACKAGES += \\\n')
        print ('---write new_packages for talpa.mk---')
        for na in new_packagesapp:   
            talpa_mk_file_object_lines.write('    '+na+' \\\n')
            print ('---write new_packagesadd for talpa.mk---'+str(na))
    if len(oscopy_files)>0:  
        talpa_mk_file_object_lines.write('#copy_files'+'\n'+'PRODUCT_COPY_FILES += \\\n')
        print ('---write copy_files for talpa.mk---')
        for cpf in oscopy_files: 
            talpa_mk_file_object_lines.write('    vendor/talpa/copy_files/'+cpf+':'+cpf+' \\\n')
            print ('---write copy_files for talpa.mk---'+str(cpf))
    if len(osincodefile)>0:   
        talpa_mk_file_object_lines.write('#incode_files'+'\n'+'PRODUCT_PACKAGE_OVERLAYS := \\\n')
        print ('---write incodefiles add for talpa.mk start---')
	print ('---vendor/talpa/incodefile/overlay---')
        talpa_mk_file_object_lines.write('    vendor/talpa/incodefile/overlay\n') 
        print ('---write incodefiles add for talpa.mk  end---')
    talpa_mk_file_object_lines.write('#Androidmk_end'+'\n')
    print ('---write Androidmk_end for talpa.mk---')
    print ('------end write  talpa.mk------')
if __name__ == '__main__':
    setevinfo()
    pack_osapp_zip()
