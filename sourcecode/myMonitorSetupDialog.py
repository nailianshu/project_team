import yaml
import cv2
import datetime
import os
from PyQt5.QtWidgets import QDialog, QFileDialog
from PyQt5.QtGui import QPixmap
from MonitorSetupDialog import Ui_BeltMonitorForm
from ZImageLabel import DrawShape


class MyMonitorSetupDialog(QDialog, Ui_BeltMonitorForm):
    def __init__(self, beltID, cfgfile, parent=None):
        super(MyMonitorSetupDialog, self).__init__(parent)
        self.setupUi(self)

        self.beltID = beltID
        self.beltID_str = 'belt_' + str(beltID)
        self.cfgfile = cfgfile
        self.snapshot_file = None
        self.pixmap = None

        # 读配置文件（仅读取默认URL，不填充其他配置到界面）
        try:
            f = open(cfgfile)
            self.cfg = yaml.load(f, Loader=yaml.FullLoader)
            f.close()
            # 填充默认的URL
            if self.beltID_str in self.cfg and 'url' in self.cfg[self.beltID_str]:
                self.lineEdit_url.setText(str(self.cfg[self.beltID_str]['url']))
        except BaseException as e:
            print(e)
            self.cfg = {}

        # 信号与槽连接
        self.radioButton_left.toggled.connect(self.setShape)
        self.radioButton_right.toggled.connect(self.setShape)
        self.label_snapshot.borderDrewSig.connect(self.borderDrew)
        self.label_snapshot.borderClearSig.connect(self.clearBorder)
        self.pushButton_save.clicked.connect(self.saveConfig)
        self.pushButton_grab.clicked.connect(self.getSnapshot)
        self.pushButton_open.clicked.connect(self.openSnapshot)

    def setShape(self):
        if self.radioButton_left.isChecked():
            self.label_snapshot.setShape(DrawShape.LEFT_BORDER)
        if self.radioButton_right.isChecked():
            self.label_snapshot.setShape(DrawShape.RIGHT_BORDER)

    def borderDrew(self, leftorright: bool, coord: list):
        if leftorright:  # 左边界
            self.lineEdit_leftborder.setText(str(coord))
        else:  # 右边界
            self.lineEdit_rightborder.setText(str(coord))

    def clearBorder(self):
        self.lineEdit_leftborder.setText("")
        self.lineEdit_rightborder.setText("")

    def getSnapshot(self):
        url = self.lineEdit_url.text().strip()
        if not url:
            print("请先输入RTSP URL")
            return
        cap = cv2.VideoCapture(url)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                snapshot_dir = './snapshot'
                if not os.path.exists(snapshot_dir):
                    os.makedirs(snapshot_dir)
                timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
                self.snapshot_file = os.path.join(snapshot_dir, f'belt_{self.beltID}_{timestamp}.jpg')
                cv2.imwrite(self.snapshot_file, frame)
                self.pixmap = QPixmap(self.snapshot_file)
                self.label_snapshot.resize(self.pixmap.size())
                self.label_snapshot.setPixmapT(self.pixmap)
        cap.release()

    def openSnapshot(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "打开快照", "./snapshot", "Images (*.png *.jpg *.bmp)")
        if file_name:
            self.pixmap = QPixmap(file_name)
            self.snapshot_file = file_name
            self.label_snapshot.resize(self.pixmap.size())
            self.label_snapshot.setPixmapT(self.pixmap)

    def saveConfig(self):
        # 写配置文件
        if self.beltID_str not in self.cfg:
            self.cfg[self.beltID_str] = {}
        self.cfg[self.beltID_str]['size'] = {}
        if self.pixmap is not None:
            self.cfg[self.beltID_str]['size']['width'] = self.pixmap.width()
            self.cfg[self.beltID_str]['size']['height'] = self.pixmap.height()
        else:
            self.cfg[self.beltID_str]['size']['width'] = 1920
            self.cfg[self.beltID_str]['size']['height'] = 1080

        url_text = self.lineEdit_url.text().strip()
        if url_text:
            if url_text.isdigit():
                self.cfg[self.beltID_str]['url'] = int(url_text)
            else:
                self.cfg[self.beltID_str]['url'] = url_text
        else:
            self.cfg[self.beltID_str]['url'] = ''

        if self.snapshot_file:
            self.cfg[self.beltID_str]['snapshot'] = self.snapshot_file
        else:
            self.cfg[self.beltID_str]['snapshot'] = ''

        belt_width_text = self.lineEdit_beltwidth.text().strip()
        self.cfg[self.beltID_str]['belt_width'] = int(belt_width_text) if belt_width_text else 180

        angle_text = self.lineEdit_angle.text().strip()
        self.cfg[self.beltID_str]['angle_alarm'] = float(angle_text) if angle_text else 6.0

        dist_text = self.lineEdit_dist.text().strip()
        self.cfg[self.beltID_str]['dist_alarm'] = float(dist_text) if dist_text else 5.0

        self.cfg[self.beltID_str]['border_left'] = self.label_snapshot.getLeftBorder()
        self.cfg[self.beltID_str]['border_right'] = self.label_snapshot.getRightBorder()

        # 确保conf目录存在
        conf_dir = os.path.dirname("./conf/config.yaml")
        if not os.path.exists(conf_dir):
            os.makedirs(conf_dir)

        with open("./conf/config.yaml", "w") as f:
            yaml.dump(self.cfg, f)
        print(self.cfg)