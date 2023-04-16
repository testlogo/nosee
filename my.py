import configparser
import cv2
import numpy as np
import pyautogui
import time

# 读取配置文件
config = configparser.ConfigParser()
config.read('config.ini')

# 从配置文件中获取参数
x = int(config.get('region', 'x'))
y = int(config.get('region', 'y'))
w = int(config.get('region', 'w'))
h = int(config.get('region', 'h'))
threshold = int(config.get('detection', 'threshold'))
dilate_iterations = int(config.get('detection', 'dilate_iterations'))
minimum_movement_pixels = int(config.get('detection', 'minimum_movement_pixels'))
switch_interval = float(config.get('switching', 'interval'))
# 设置区域的坐标和大小
# x, y, w, h = 50, 50, 500, 70

# 创建一个VideoCapture对象，打开默认的摄像头
cap = cv2.VideoCapture(0)

# 初始化背景模型和标志变量
background = None
is_desktop = False
last_switch_time = 0

# 循环读取帧
while True:
    # 读取当前帧
    ret, frame = cap.read()

    # 如果无法读取帧，退出循环
    if not ret:
        break

    # 将帧转换为灰度图像
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 如果背景模型未初始化，使用当前帧作为背景
    if background is None:
        background = gray

    # 计算当前帧与背景之间的差异
    diff = cv2.absdiff(background, gray)

    # 对差异图像进行阈值处理，过滤掉微小的变化
    thresh = cv2.threshold(diff, threshold, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=dilate_iterations)

    # 在区域内检测是否有变化
    roi = thresh[y : y + h, x : x + w]
    movement_detected = cv2.countNonZero(roi) > minimum_movement_pixels
    print(f"movement_detected:{movement_detected}")
    # 如果检测到有变化，触发屏幕切换
    if movement_detected:
        if not is_desktop:
            is_desktop = True
            pyautogui.keyDown('win')
            pyautogui.keyDown('d')
            # pyautogui.press('right')
            pyautogui.keyUp('win')
            pyautogui.keyUp('d')
            last_switch_time = time.time()

    # 如果未检测到变化，且上次检测到变化的时间超过2秒，维持当前状态
    elif not movement_detected and (time.time() - last_switch_time) > switch_interval:
        if  is_desktop:
            is_desktop = False
            pyautogui.keyDown('win')
            pyautogui.keyDown('d')
            # pyautogui.press('right')
            pyautogui.keyUp('win')
            pyautogui.keyUp('d')
            last_switch_time = time.time()

    # 在帧上绘制区域的边界框
    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # 显示帧
    cv2.imshow("frame", frame)

    # 按下q键退出循环
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
    if cv2.getWindowProperty('frame', cv2.WND_PROP_VISIBLE) < 1.0: 
        break

# 释放资源
cap.release()
cv2.destroyAllWindows()
