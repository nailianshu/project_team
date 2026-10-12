from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QApplication, QAction, QMdiArea, QMdiSubWindow
import sys

from myBeltMonitor import MyBeltMonitorForm
from myMonitorSetupDialog import MyMonitorSetupDialog


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.mdi = QMdiArea()
        self.setCentralWidget(self.mdi)

        exitAction = QAction( "退出", self)
        exitAction.setShortcut("Ctrl+Q")
        exitAction.triggered.connect(self.close)

        self.fileMenu = self.menuBar().addMenu("文件")
        self.fileMenu.addAction(exitAction)

        self.monitorMenu = self.menuBar().addMenu("监控窗口")

        self.belt1Action = QAction(QIcon("./icons/camera_belt1.png"), "皮带1", self, checkable=True)
        self.belt1Action.setToolTip("打开皮带1摄像头")
        self.belt1Action.triggered.connect(self.addBelt1Monitor)
        self.belt1Action.setChecked(False)
        self.monitorMenu.addAction(self.belt1Action)

        self.belt2Action = QAction(QIcon("./icons/camera_belt2.png"), "皮带2", self, checkable=True)
        self.belt2Action.setToolTip("打开皮带2摄像头")
        self.belt2Action.triggered.connect(self.addBelt2Monitor)
        self.belt2Action.setChecked(False)
        self.monitorMenu.addAction(self.belt2Action)

        self.belt3Action = QAction(QIcon("./icons/camera_belt3.png"), "皮带3", self, checkable=True)
        self.belt3Action.setToolTip("打开皮带3摄像头")
        self.belt3Action.triggered.connect(self.addBelt3Monitor)
        self.belt3Action.setChecked(False)
        self.monitorMenu.addAction(self.belt3Action)

        #toolbar
        tool_monitor = self.addToolBar("监控")
        tool_monitor.addAction(self.belt1Action)
        tool_monitor.addAction(self.belt2Action)
        tool_monitor.addAction(self.belt3Action)

        # 系统配置菜单
        self.configMenu = self.menuBar().addMenu("系统配置")
        confBelt1Action = QAction(QIcon("./icons/conf_belt1.png"), "配置皮带1", self)
        confBelt1Action.setToolTip("配置皮带1")
        confBelt1Action.triggered.connect(self.confBelt1)
        self.configMenu.addAction(confBelt1Action)

        confBelt2Action = QAction(QIcon("./icons/conf_belt2.png"), "配置皮带2", self)
        confBelt2Action.setToolTip("配置皮带2")
        confBelt2Action.triggered.connect(self.confBelt2)
        self.configMenu.addAction(confBelt2Action)

        confBelt3Action = QAction(QIcon("./icons/conf_belt3.png"), "配置皮带3", self)
        confBelt3Action.setToolTip("配置皮带3")
        confBelt3Action.triggered.connect(self.confBelt3)
        self.configMenu.addAction(confBelt3Action)

        # 配置工具栏
        tool_config = self.addToolBar("配置")
        tool_config.addAction(confBelt1Action)
        tool_config.addAction(confBelt2Action)
        tool_config.addAction(confBelt3Action)


    def addBelt1Monitor(self, state):
        if state:
            self.belt1Monitor = QMdiSubWindow()
            self.belt1Monitor.setWidget(
                MyBeltMonitorForm(0, './conf/config.yaml'))
            self.belt1Monitor.setWindowTitle("皮带1")
            self.belt1Monitor.setWindowIcon(QIcon("./icons/camera.jpg"))
            self.belt1Monitor.setGeometry(0, 0, 1024, 768)
            self.mdi.addSubWindow(self.belt1Monitor)
            self.belt1Monitor.show()
        if not state:
            self.belt1Monitor.close()


    def addBelt2Monitor(self, state):
        if state:
            self.belt2Monitor = QMdiSubWindow()
            self.belt2Monitor.setWidget(
                MyBeltMonitorForm(1, './conf/config.yaml'))
            self.belt2Monitor.setWindowTitle("皮带2")
            self.belt2Monitor.setWindowIcon(QIcon("./icons/camera.jpg"))
            self.belt2Monitor.setGeometry(0, 0, 1024, 768)
            self.mdi.addSubWindow(self.belt2Monitor)
            self.belt2Monitor.show()
        if not state:
            self.belt2Monitor.close()


    def addBelt3Monitor(self, state):
        if state:
            self.belt3Monitor = QMdiSubWindow()
            self.belt3Monitor.setWidget(
                MyBeltMonitorForm(2, './conf/config.yaml'))
            self.belt3Monitor.setWindowTitle("皮带3")
            self.belt3Monitor.setWindowIcon(QIcon("./icons/camera.jpg"))
            self.belt3Monitor.setGeometry(0, 0, 1024, 768)
            self.mdi.addSubWindow(self.belt3Monitor)
            self.belt3Monitor.show()
        if not state:
            self.belt3Monitor.close()

    def confBelt1(self):
        dialog = MyMonitorSetupDialog(0, './conf/config.yaml', self)
        dialog.setModal(True)
        dialog.setWindowIcon(QIcon("./icons/conf.png"))
        dialog.exec_()

    def confBelt2(self):
        dialog = MyMonitorSetupDialog(1, './conf/config.yaml', self)
        dialog.setModal(True)
        dialog.setWindowIcon(QIcon("./icons/conf.png"))
        dialog.exec_()

    def confBelt3(self):
        dialog = MyMonitorSetupDialog(2, './conf/config.yaml', self)
        dialog.setModal(True)
        dialog.setWindowIcon(QIcon("./icons/conf.png"))
        dialog.exec_()





if __name__ == '__main__':
    app = QApplication(sys.argv)
    my_window = MainWindow()
    my_window.setWindowTitle("皮带监控")
    my_window.showMaximized()
    sys.exit(app.exec_())
