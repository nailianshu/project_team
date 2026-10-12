import sys
import datetime
import yaml

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import *
from PyQt5.Qt import QThread
import numpy as np
import cv2
from ultralytics import YOLO
import torch

# 计算偏移距离和偏移角度
from BeltMonitor import Ui_BeltMonitorForm

from alg import get_border, calculate_angle, calculate_dist, mid_line


#
# def cal_distance_degree(frame):
#     return 1.0, 2.0

# 识别皮偏移的角度和偏移距离
class MyBeltProcess(QThread):
    # 信号参数: frame, distance, angle
    done_signal = pyqtSignal(np.ndarray, float, float)

    def __init__(self, cfg):
        super(MyBeltProcess, self).__init__()
        self.runFlag = True
        self.cfg = cfg

    def stop(self):
        self.runFlag = False

    def run(self):
        url = self.cfg['url']
        self.cap = cv2.VideoCapture(url)
        
        self.model = YOLO('./model/best.pt')
        
        border_left = self.cfg['border_left']
        border_right = self.cfg['border_right']
        belt_width = self.cfg['belt_width']
        
        has_border = len(border_left) == 2 and len(border_right) == 2
        
        if has_border:
            border_left_p0 = tuple(border_left[0])
            border_left_p1 = tuple(border_left[1])
            border_right_p0 = tuple(border_right[0])
            border_right_p1 = tuple(border_right[1])
        else:
            border_left_p0 = None
            border_left_p1 = None
            border_right_p0 = None
            border_right_p1 = None
        
        while self.runFlag:
            success, frame = self.cap.read()
            if success:
                # from yolo_seg1.py
                device = "cuda:0" if torch.cuda.is_available() else "cpu"
                results = self.model.predict(frame, device=device)
                # results = self.model.predict(frame, device="cuda:0")
                result = results[0]  # 只有1帧
                boxes = result.boxes
                cls = boxes.cls
                masks = result.masks
                pixel_coords = masks.xy
                distance = 0.0
                degree = 0.0
                if has_border and len(pixel_coords) == 1 and cls[0].item() == 0:  # found one border of belt
                    pts = np.asarray(pixel_coords[0], dtype=np.int32)
                    keypts = cv2.approxPolyDP(pts, 10, True)
                    reco_border_left, reco_border_right = get_border(keypts, border_left_p0, border_left_p1, border_right_p0, border_right_p1)
                    if reco_border_left is not None and reco_border_right is not None:
                        reco_mid_line = mid_line(reco_border_left, reco_border_right)
                        org_mid_line = mid_line((border_left_p0, border_left_p1), (border_right_p0, border_right_p1))
                        if reco_mid_line[0] is not None and reco_mid_line[1] is not None and \
                                org_mid_line[0] is not None and org_mid_line[1] is not None:
                            degree = calculate_angle(org_mid_line, reco_mid_line)
                            distance = calculate_dist(org_mid_line, reco_mid_line, (border_left_p0, border_left_p1),
                                                      (border_right_p0, border_right_p1), belt_width)
                            # cv2.drawContours(frame, [keypts], 0, (0, 0, 255), 1)

                            cv2.line(frame, border_left_p0, border_left_p1, (0, 255, 0), 1)  # org_border_left
                            cv2.line(frame, border_right_p0, border_right_p1, (0, 255, 0), 1)  # org_boder_right
                            cv2.line(frame, org_mid_line[0], org_mid_line[1], (0, 255, 0), 1)  # org_mid_line

                            cv2.line(frame, reco_border_left[0], reco_border_left[1], (0, 0, 255),
                                     1)  # reco_border_left
                            cv2.line(frame, reco_border_right[0], reco_border_right[1], (0, 0, 255),
                                     1)  # reco_boder_right
                            cv2.line(frame, reco_mid_line[0], reco_mid_line[1], (0, 0, 255), 1)  # reco_mid_line

                # end from yolo_seg1.py

                # cv2.putText(frame, 'distance:'+str(distance)+'/degree:'+str(degree),
                #             (int(frame.shape[1]/2), int(frame.shape[0]/2)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255,0))
                self.done_signal.emit(frame, distance, degree)
                # 识别皮带边缘
                QThread.msleep(int(1000 / 25))

        self.cap.release()


class MyBeltMonitorForm(QWidget, Ui_BeltMonitorForm):
    def __init__(self, beltID, cfgFile):
        super(MyBeltMonitorForm, self).__init__()
        self.setupUi(self)

        self.beltID = beltID
        self.beltID_str = 'belt_' + str(beltID)
        
        with open(cfgFile, 'r', encoding='utf-8') as f:
            self.cfg_data = yaml.load(f, Loader=yaml.FullLoader)
        
        belt_cfg = self.cfg_data[self.beltID_str]

        self.processThread = MyBeltProcess(belt_cfg)
        self.processThread.done_signal.connect(self.refreshFrame)
        self.processThread.start()

    # frame：原始图像
    # new_frame: 画界面后的图像
    # angle：偏移角度
    # distance: 偏移距离
    def refreshFrame(self, frame, distance, angle):
        self.lcdNumber_distance.display(distance)
        self.lcdNumber_angle.display(angle)

        self.label_info.setText('读帧成功')
        self.label_timestamp.setText(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        row, col, pix = frame.shape[0], frame.shape[1], frame.strides[0]
        qImg = QImage(frame.data, col, row, pix, QImage.Format_RGB888).rgbSwapped()
        pixmap = QPixmap.fromImage(qImg)
        size = self.label_img.size()
        self.label_img.setPixmap(pixmap.scaled(size, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def startWriteVideo(self):
        print('startWriteVideo')

    def writeSnapshot(self):
        print('writeSnapshot')

    def openVideoFile(self):
        print('openVidoFile')