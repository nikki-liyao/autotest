# -*- coding: utf-8 -*-
import cv2
import numpy as np
import imutils
import os.path
import time
import re
from PIL import Image
import pytesseract
from auto_adb import auto_adb
from config import lixing_list

adb = auto_adb()


def _get_screen_height():#获取安卓屏幕的高
    size_str = adb.get_screen()
    m = re.search(r'(\d+)x(\d+)', size_str)
    if m:
        return int(m.group(2)) #group 2不懂
    return 1920

def _get_screen_width():#获取安卓屏幕的宽
    size_str = adb.get_screen()
    m = re.search(r'(\d+)x(\d+)', size_str)
    if m:
        return int(m.group(1))
    return 1080

def text_same_with_max_three_error(text1, text2):#程序获取到的文字和实际的文字对比 最多3个误差
    if len(text2) < 3:
        return False
    error_count = 0
    length = min(len(text1),len(text2))
    for i in range(length):
        if text1[i] != text2[i]:
            error_count = error_count+1
            if error_count > 2:
                return False
    return True

def find_search(boxList, index):#获取type文字的位置
    if (boxList[index + 0].split(' ')[0] == 'T' and
          boxList[index + 1].split(' ')[0] == 'y' and
          boxList[index + 2].split(' ')[0] == 'p' and
          boxList[index + 3].split(' ')[0] == 'e'):
        print('find Search or Type URL')
        return True
def take_screenshot(pic_count):#获取图片文字信息
    adb.run('shell screencap -p /sdcard/autojump.png')
    cmd = 'pull /sdcard/autojump.png ./pic/{x1}.png'.format(x1=pic_count)
    adb.run(cmd)


def pull_screenshot():#获取图片文字信息
    adb.run('shell screencap -p /sdcard/autojump.png')
    adb.run('pull /sdcard/autojump.png .')
    return Image.open('./autojump.png')


# def find_position(appName):
#     main_image = pull_screenshot()
#     height = _get_screen_height()
#
#     region = (int(main_image.width * 0.23), 0, int(main_image.width / 2), height)
#     cropImg = main_image.crop(region)
#     try:
#         boxes = pytesseract.image_to_boxes(cropImg)
#         boxList = boxes.splitlines()
#         length = len(boxList)
#         for index in range(length):
#             if find_our_company(boxList, index):
#                 box = boxList[index].split(' ')
#                 region2 = (int(main_image.width * 0.23), height - int(box[4]) - int(_get_screen_width()*0.08), main_image.width, height - int(box[4]))
#                 cropImg2 = main_image.crop(region2)
#                 text = pytesseract.image_to_string(cropImg2)
#                 print(text)
#                 if text_same_with_max_three_error(appName, text):
#                     return int(main_image.width * 0.23), height - int(box[2])
#     except Exception as ex:
#         print('image_to_boxes Exception:' + str(ex))
#     print('not found...')
#     return -1, -1


def find_input_position():#找到输入框
    main_image = pull_screenshot()

    rgb_im = main_image.convert('RGB')


    hei = int(main_image.height / 4)
    for i in range(hei):
        r, g, b = rgb_im.getpixel((500, i))
        sum = (b - 245) * (b - 245) + (g - 243) * (g - 243) + (r - 242) * (r - 242)
        if(sum < 100):
            return i
    return -1

def find_image_position(template, appicon):#找 downloadyes 和 downloadno
    (height, width) = template.shape[:2]
    # open the main image and convert it to gray scale image
    main_image = pull_screenshot()
    gray_image = cv2.cvtColor(main_image, cv2.COLOR_BGR2GRAY)
    temp_found = None
    cur_scale = 0
    for scale in np.linspace(0.2, 1.0, 20)[::-1]:
        # resize the image and store the ratio
        resized_img = imutils.resize(gray_image, width=int(gray_image.shape[1] * scale))
        ratio = gray_image.shape[1] / float(resized_img.shape[1])
        if resized_img.shape[0] < height or resized_img.shape[1] < width:
            break
        # Convert to edged image for checking
        e = cv2.Canny(resized_img, 10, 25)
        match = cv2.matchTemplate(e, template, cv2.TM_CCOEFF)
        (_, val_max, _, loc_max) = cv2.minMaxLoc(match)
        if temp_found is None or val_max > temp_found[0]:
            temp_found = (val_max, loc_max, ratio)
            cur_scale = scale
    # Get information from temp_found to compute x,y coordinate
    (_, loc_max, r) = temp_found
    (x_start, y_start) = (int(loc_max[0]), int(loc_max[1]))
    (x_end, y_end) = (int((loc_max[0] + width)), int((loc_max[1] + height)))
    x_start_origin = int(x_start / cur_scale)
    y_start_origin = int(y_start / cur_scale)
    get_color_y_start = y_start_origin + 42
    color = main_image[get_color_y_start, x_start_origin + 3]
    print(color)
    sum = 10000
    if (appicon == downloadyes):
        sum = (color[2] - 56) * (color[2] - 56) + (color[1] - 56) * (color[1] - 56) + (color[0] - 255) * (color[0] - 255)
    elif (appicon == downloadno):
        sum = (color[2] - 255) * (color[2] - 255) + (color[1] - 180) * (color[1] - 180) + (color[0] - 41) * (color[0] - 41)
    print(sum)
    if (sum < 100):
        return x_start_origin, y_start_origin
    else:
        print('not found...')
        return -1, -1


cur_dir = os.path.dirname(os.path.realpath(__file__))

appList = []
downloadyes = 'downloadyes.png'
downloadno = 'downloadno.png'
def lixing_with_keyword(keyword):
    adb.run('shell monkey -p video.downloader.videodownloader 1')
    time.sleep(8)

    ypos = find_input_position()
    if(ypos==-1):
        #可能是广告,按下返回键把广告关闭掉再重试
        adb.run('shell input keyevent 4')  # 4 -->  "KEYCODE_BACK"
        time.sleep(8)
        ypos = find_input_position()
        if(ypos==-1):
            print('切换语言为英文后重试...')
            return
    adb.run('shell input tap 500 {y1}'.format(y1=ypos))

    time.sleep(3)
    cmd = 'shell input text {y1}'.format(y1=keyword)
    adb.run(cmd)
    adb.run('shell input keyevent 66')  # 66 -->  "KEYCODE_ENTER"
    time.sleep(20)

    template = cv2.imread(downloadyes)
    template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    template = cv2.Canny(template, 10, 25)
    
    xpos, ypos = find_image_position(template, downloadyes)
    if (xpos == -1):
        print(keyword)
    else:
        cmd = 'shell input tap {x1} {y1}'.format(x1=xpos, y1=ypos)
        adb.run(cmd)
        time.sleep(1)
    adb.run('shell input keyevent 4')  # 4 -->  "KEYCODE_BACK"
    adb.run('shell input keyevent 4')  # 4 -->  "KEYCODE_BACK"
    adb.run('shell input keyevent 4')  # 4 -->  "KEYCODE_BACK"
    adb.run('shell input keyevent 4')  # 4 -->  "KEYCODE_BACK"
    adb.run('shell input keyevent 4')  # 4 -->  "KEYCODE_BACK"

pytesseract.pytesseract.tesseract_cmd = 'Tesseract-OCR\\tesseract.exe'

keywords = lixing_list.split('\n')
for keyword in keywords:
    if keyword.strip() == '':
        continue
    print(keyword)
    lixing_with_keyword(keyword)
