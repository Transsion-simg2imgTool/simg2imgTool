#!/bin/bash
# ant 编译后执行脚本
:'
引用参数：
    1.GITtalpa_appsREPOURL = ssh://ostest@10.250.119.10:29418/talpa_apps && scp -p -P 29418 ostest@10.250.119.10:hooks/commit-msg talpa_apps/.git/hooks/
    2.WORKSPACE = 
    3.JENKINSWORKSPACE = /work/workspace/jenkins/proj
    4.JOB_NAME = launcher（等等）
'


WORKSPACE=$WORKSPACE #代码存放根目录
GITtalpa_appsREPOURL=$GITtalpa_appsREPOURL
JENKINSWORKSPACE=$JENKINSWORKSPACE
JOB_NAME=$JOB_NAME
APKVERSION='V0.0.0'
APKVERSIONTEM='V0.0.1'
echo "WORKSPACE:"$WORKSPACE    #打印出代码仓库目录
echo "JENKINSWORKSPACE:"$JENKINSWORKSPACE #打印出jenkins工作目录
echo "GITtalpa_appsREPOURL:"$GITtalpa_appsREPOURL #打印出talpa_apps仓库目录
BUILD='False'
if [ ! -d "$JENKINSWORKSPACE/talpa_apps" ];then #判断$JENKINSWORKSPACE/talpa_apps文件夹是否不存在
	mkdir -p $JENKINSWORKSPACE/talpa_apps       #不存在,就创建一个
	cd $JENKINSWORKSPACE/talpa_apps             #进入到该文件夹
	git clone $GITtalpa_appsREPOURL;            #将talpa_apps clone下来
	cd -                                        #返回到上一次的工作目录
fi
if [ ! -d "$WORKSPACE" ];then                   #判断$WORKSPACE文件夹是否不存在
	echo "You project file not exist! Please commit  file by Yourselfe!" #不存在，打印提示信息，并退出
	exit 1
else
	APKVERSION=$(find $WORKSPACE/code/$JOB_NAME/ -name AndroidManifest.xml -exec grep "android:versionName=*" {} \;) #搜索指定目录下AndroidManifest.xml文件中含有'android:versionName='的一行
	APKVERSION=${APKVERSION##*=}   #去掉最后一个'='及其左边的字符 赋值给 APKVERSION
	APKVERSION=$(echo $APKVERSION |sed 's/\"//g')  #去除APKVERSION字符中的所有 "
	APKVERSION=$(echo $APKVERSION |sed 's/[\>]//g') #去除APKVERSION字符中的所有 >
	APKVERSION=$(echo $APKVERSION |sed 's/[[:space:]]//g') #去除APKVERSION字符中的所有空格、空白字符、tab
	echo "APKVERSION:"$APKVERSION       #打印出获取到的版本号
	if [ ! -d "/work/OSTeam/simg2img/talpa_apps_backup/$JOB_NAME/$APKVERSION/" ];then  #如果/work/OSTeam/simg2img/talpa_apps_backup/$JOB_NAME/$APKVERSION/文件夹不存在
		mkdir -p /work/OSTeam/simg2img/talpa_apps_backup/$JOB_NAME/$APKVERSION/   #创建对应模块的具体版本号的文件夹
		find $WORKSPACE/code/$JOB_NAME/ -name '*.apk' -exec cp {} /work/OSTeam/simg2img/talpa_apps_backup/$JOB_NAME/$APKVERSION/$JOB_NAME''_''$APKVERSION''.apk \; #find 编译后输出的apk文件，拷贝到指定目录下并重命名
		cp -raf $WORKSPACE/code/$JOB_NAME/Android.mk /work/OSTeam/simg2img/talpa_apps_backup/$JOB_NAME/$APKVERSION/  #拷贝代码仓库下的Android.mk文件到输出目录下
		if [ -d "$WORKSPACE/code/lib" ];then #如果存在lib文件夹
			cp -raf $WORKSPACE/code/lib /work/OSTeam/simg2img/talpa_apps_backup/$JOB_NAME/$APKVERSION/ #拷贝lib文件夹到指定输出目录下
		fi
		cd /work/OSTeam/simg2img/talpa_apps_backup/$JOB_NAME/$APKVERSION/  #进入到输出目录下
		apkname=$JOB_NAME''_''$APKVERSION''.apk  #apk文件名称
		sed -i 's/LOCAL_SRC_FILES     := [A-Za-z0-9_]*.*/LOCAL_SRC_FILES     := '$apkname'/g' Android.mk  #修改Android.mk文件中的LOCAL_SRC_FILES的内容
		cd -  #返回上一个工作目录
	fi
fi

if [ -f "$WORKSPACE/Readme.txt" ];then #如果代码仓库下存在Readme.txt文件，发布标志位 置true
	BUILD='True'
fi
echo "BUILD:"$BUILD   #打印出发布标志位
if [ $BUILD == 'True' ];then  #如果发布标志位为true
	APKVERcheckSION='demo'         
	firstline='Readmefirstline'
	checktag='CodeGittag'
	firstline=`head -1 $WORKSPACE/Readme.txt |grep -o "[^ ]\+\( \+[^ ]\+\)*"`  #读取Readme.txt文件第一行内容 并通过grep 正则匹配
	firstline=${firstline##*=}
	firstline=$(echo $firstline |sed 's/\"//g')
	firstline=$(echo $firstline |sed 's/" ﻿0"/"0"/g')
	cd $WORKSPACE
	checktag=`git tag |grep $firstline |grep -o "[^ ]\+\( \+[^ ]\+\)*"`
	checktag=${checktag##*=}
	checktag=$(echo $checktag |sed 's/\"//g')
	echo 'checktag:'$checktag
	echo 'firstline:'$firstline
	if [ "$checktag"!="" -a "$firstline"!="" ];then
		if [ $firstline == $checktag ];
		then
			if [ ! -d "$JENKINSWORKSPACE/talpa_apps/$JOB_NAME/" ];then
				mkdir -p $JENKINSWORKSPACE/talpa_apps/$JOB_NAME/
			fi
			if [ ! -d "$JENKINSWORKSPACE/talpa_apps/$JOB_NAME/$firstline/" ];then
				mkdir -p $JENKINSWORKSPACE/talpa_apps/$JOB_NAME/$firstline/
			fi
			cp -raf $WORKSPACE/Readme.txt $JENKINSWORKSPACE/talpa_apps/$JOB_NAME/$firstline/
			git reset --hard;
			git clean -fdx;
			git pull
			git checkout $firstline;
			APKVERcheckSION=$(find $WORKSPACE/code/$JOB_NAME/ -name AndroidManifest.xml -exec grep "android:versionName=*" {} \;)
			APKVERcheckSION=${APKVERcheckSION##*=}
			APKVERcheckSION=$(echo $APKVERcheckSION |sed 's/\"//g')
			APKVERcheckSION=$(echo $APKVERcheckSION |sed 's/[\>]//g')
			APKVERcheckSION=$(echo $APKVERcheckSION |sed 's/[[:space:]]//g')
			APKVERSIONCODE=$(find $WORKSPACE/code/$JOB_NAME/ -name AndroidManifest.xml -exec grep "android:versionCode=*" {} \;)
			APKVERSIONCODE=${APKVERSIONCODE##*=}
			APKVERSIONCODE=$(echo $APKVERSIONCODE |sed 's/\"//g')
			APKVERSIONCODE=$(echo $APKVERSIONCODE |sed 's/[\>]//g')
			APKVERSIONCODE=$(echo $APKVERSIONCODE |sed 's/[[:space:]]//g')
			demook=$(echo $APKVERcheckSION|cut -d "." -f 3)
			echo "APKVERSIONCODE:"$APKVERSIONCODE
			echo 'APKVERcheckSION:'$APKVERcheckSION
			echo "demook:"$demook
			if [ $APKVERSIONCODE != $demook ];then
				echo "You project APKVERSIONCODE != APKVERcheckSIONNAME,Please Check YourProject's AndroidManifest.xml"
				exit 0
			fi
			if [ $APKVERcheckSION == $firstline ];then
				mkdir -p $JENKINSWORKSPACE/talpa_apps/$JOB_NAME/$APKVERcheckSION/
				cp -raf /work/OSTeam/simg2img/talpa_apps_backup/$JOB_NAME/$APKVERcheckSION/$JOB_NAME''_''$APKVERcheckSION''.apk $JENKINSWORKSPACE/talpa_apps/$JOB_NAME/$APKVERcheckSION/
				cp -raf /work/OSTeam/simg2img/talpa_apps_backup/$JOB_NAME/$APKVERcheckSION/Android.mk $JENKINSWORKSPACE/talpa_apps/$JOB_NAME/$APKVERcheckSION/
				cd $JENKINSWORKSPACE/talpa_apps/$JOB_NAME/$APKVERcheckSION/
				APKVERSIONTEM=$(find $JENKINSWORKSPACE/talpa_apps/$JOB_NAME/$APKVERcheckSION/ -name Android.mk -exec grep "LOCAL_SRC_FILES" {} \;)
				APKVERSIONTEM=${APKVERSIONTEM##*:=}
				if [ ! $APKVERSIONTEM == "$JOB_NAME''_''$APKVERcheckSION''.apk" ];then
					apkname=$JOB_NAME''_''$APKVERcheckSION''.apk
					sed -i 's/LOCAL_SRC_FILES     := [A-Za-z0-9_]*.*/LOCAL_SRC_FILES     := '$apkname'/g' Android.mk
				fi
				if [ -d "/work/OSTeam/simg2img/talpa_apps_backup/$JOB_NAME/$APKVERcheckSION/lib" ];then
					cp -raf /work/OSTeam/simg2img/talpa_apps_backup/$JOB_NAME/$APKVERcheckSION/lib $JENKINSWORKSPACE/talpa_apps/$JOB_NAME/$APKVERcheckSION/
				fi
				cd $JENKINSWORKSPACE/talpa_apps/
				git checkout master
				git config --global user.email "3033798168@qq.com";
				git config --global user.name "ostest";
				git add --all;
				git commit -s -m "add $JOB_NAME'_'$APKVERcheckSION'_'Apk ";
				git push origin master
			fi
		else
			exit 1
		fi
	else
		exit 1
	fi
fi
