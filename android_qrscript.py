#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Author  : xinxi
@Time    : 2018/1/5 15:06
@describe: android上传apk和二维码脚本
@run: python android_qrscript.py /Users/xinxi/Documents/AndroidProject/AndroidDemo
"""
import qrcode,os,time,subprocess,sys,requests,json
from PIL import Image

is_debug = False

if is_debug:
   upload_apk_url = 'http://127.0.0.1:5000/apk/uploadapk'
   upload_qrcode_url = 'http://127.0.0.1:5000/apk/uploadqrcode'
   upload_apkinfo_url = 'http://127.0.0.1:5000/apk/uploadapkinfo'

else:
   upload_apk_url = 'http://home.nickxin.top:7777/apk/uploadapk'
   upload_qrcode_url = 'http://home.nickxin.top:7777/apk/uploadqrcode'
   upload_apkinfo_url = 'http://home.nickxin.top:7777/apk/uploadapkinfo'


def make_qrcode(url):
    '''
    生成二维码
    :param url:
    :return:
    '''
    print('开始生成二维码...')
    img = qrcode.QRCode(
        version=2,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=8,
        border=2
    )
    img = qrcode.make(url)
    base_path = os.path.abspath(os.path.dirname(__file__))
    print(base_path)
    save_image_folder = os.path.join(base_path,'qrcode_images')
    print(save_image_folder)
    if not os.path.exists(save_image_folder):
        os.mkdir(save_image_folder)
        print("创建保存文件夹:{}".format(save_image_folder))
    else:
        print("已存在不需要创建...")
    create_time = time.strftime("%Y%m%d%H%M%S")
    save_image_path = os.path.join(save_image_folder,create_time + "_" + "app.png")
    img.save(save_image_path)
    return save_image_path


def upload_local_qrcode(qrcode_path):
    '''
    上传本地生成apk
    :param filepath:
    :return:
    '''
    print("qrcode本地路径:{}".format(qrcode_path))
    response_remote_path = ''
    try:
        files = {'qrcode': open(qrcode_path, 'rb')}
        response = requests.post(upload_qrcode_url,files=files, verify=False)
        response_remote_path = str(response.json()['filename'])
        if response.status_code == 200 and response_remote_path.startswith('http'):
            print('报告上传本地生成qrcode成功!')
            print('保存在服务器地址:{}'.format(response_remote_path))
    except Exception as e:
        print('上传qrcode异常!{}'.format(e))
    finally:
        return response_remote_path


def upload_local_apk(apk_path):
    '''
    上传本地生成apk
    :param filepath:
    :return:
    '''
    print('开始上传本地生成apk!')
    print(apk_path)
    response_remote_path = ''
    try:
        files = {'apk': open(apk_path, 'rb')}
        response = requests.post(upload_apk_url, files=files, verify=False)
        print(response.json())
        response_remote_path = str(response.json()['filename'])
        if response.status_code == 200 and response_remote_path.startswith('http'):
            print('报告上传本地生成apk成功!')
            response_remote_path = response.json()['filename']
            print('保存在服务器地址:{}'.format(response_remote_path))
    except Exception as e:
        print('上传apk异常!{}'.format(e))
    finally:
        return response_remote_path


def build_script(prject_path):
    '''
    打包命令
    :return:
    '''
    current_path = os.path.abspath(os.path.dirname(__file__))
    print(current_path)
    os.chdir(prject_path)
    print("切换到项目路径")
    clean_cmd = "gradle clean"
    subprocess.call(clean_cmd, shell=True)
    print("清理环境完成...")
    build_cmd = "gradle assembleRelease"
    subprocess.call(build_cmd,shell=True)
    print("打包完成...")
    os.chdir(current_path)
    print("切换到脚本路径...")
    build_apkend_path = '/app/build/outputs/apk/release'
    apk_path = find_app(prject_path + build_apkend_path)
    print("生成apk本地路径:{}".format(apk_path))
    apk_remote_path = upload_local_apk(apk_path)
    qrcode_local_path = make_qrcode(apk_remote_path)
    qrcode_remote_path = upload_local_qrcode(qrcode_local_path)
    upload_apk_info(apk_remote_path,qrcode_remote_path)



def upload_apk_info(apk_remote_path,qrcode_remote_path):
    '''
    上传apk相关信息
    :return:
    '''
    print('开始上传apk相关信息!')
    platform = ''
    try:

        if apk_remote_path.endswith(".apk"):
            platform = 'android'
        elif apk_remote_path.endswith(".ipa") or apk_remote_path.endswith(".app") :
            platform = 'ios'
        if  platform != '':
            params = dict()
            params['platform'] = platform
            params['version'] = '1.0'
            params['env'] = 'test'
            params['apk_path'] = apk_remote_path
            params['qrcode_path'] = qrcode_remote_path
            print('参数:{}'.format(params))
            response = requests.post(upload_apkinfo_url, data=json.dumps(params), verify=False)
            print(response.json())
            if response.status_code == 200 and response.json()['status'] == 'ok':
                print('报告上传apk信息成功!')
    except Exception as e:
        print('报告上传apk信息异常!{}'.format(e))



def find_app(folder_path):
    app_path = ''
    if str(folder_path).endswith("apk"):
        app_path= folder_path
    else:
        for file in os.listdir(folder_path):
            if file.startswith('app'):
                app_path = os.path.join(folder_path,file)
                print('app路径:{}'.format(app_path))
                break
    return app_path


if __name__ == '__main__':
    prject_path = sys.argv[1]
    print("项目地址:" + prject_path )
    build_script(prject_path)





