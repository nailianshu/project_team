from PyQt5 import Qt
from PyQt5.QtGui import QPixmap, QMouseEvent, QPainter, QPen, QBrush, QResizeEvent
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt, QPoint, QPointF, QRect, QSize, pyqtSignal

from enum import Enum

class Status(Enum):
    DRAW_BEGIN = 1  #鼠标左键按下：开始划线，起点确定
    DRAW_MOVE  = 2  #鼠标移动：线段终点移动
    DRAW_DONE  = 3  #鼠标左键松下：线段终点确定，线段固定

class DrawShape(Enum):
    LEFT_BORDER = 0    #左边界线段
    RIGHT_BORDER = 1   #右边界线段


class ZImageLabel(QLabel):
    #bool:True是左边界，False是右边界
    #list:起点图像坐标和终点图像坐标组成的列表，如:[[100,100],[200,200]]
    borderDrewSig: pyqtSignal = pyqtSignal(bool, list, name="borderDrew")
    borderClearSig: pyqtSignal = pyqtSignal()
    def __init__(self, parent):
        super(ZImageLabel, self).__init__(parent)
        self._status: Status = Status.DRAW_DONE
        self._shape: DrawShape = DrawShape.LEFT_BORDER

        self._x_begin: int = 0   #划线起点坐标
        self._y_begin: int = 0
        self._mx: int = 0        #划线终点坐标
        self._my: int = 0

        self._leftborder_begin: QPointF = None
        self._leftborder_end: QPointF = None
        self._leftborder_begin_f: QPointF = None
        self._leftborder_end_f: QPointF = None
        self._leftborder_done: bool = False

        self._rightborder_begin: QPointF = None
        self._rightborder_end: QPointF = None
        self._rightborder_begin_f: QPointF = None
        self._rightborder_end_f: QPointF = None
        self._rightborder_done: bool = False

        self._pixmap: QPixmap = None  # 没有缩放的pixmap
        self._pic: QPixmap = None  # 缩放后的pixmap
        self._is_drawing: bool = True  # False
        self._vertex_mapped: bool = False
        self.setMouseTracking(True)

    def point_2_pointf(self, point: QPointF):
        ratio_x = self._pic.size().width() * 1.0 / self._pixmap.size().width()
        ratio_y = self._pic.size().height() * 1.0 / self._pixmap.size().height()
        #print(f'ratio_x:{ratio_x}, ratio_y:{ratio_y}')
        #缩放KeepAspectRatio要用以下计算公式
        #return QPointF(point.x() * ratio_x + (self.geometry().size().width() - self._pic.size().width()) / 2,
        #        point.y() * ratio_y)
        return QPointF(point.x() * ratio_x,
                       point.y() * ratio_y)

    def pointf_2_point(self, pointf: QPointF):
        ratio_x = self._pic.size().width() * 1.0 / self._pixmap.size().width()
        ratio_y = self._pic.size().height() * 1.0 / self._pixmap.size().height()
        return QPointF(pointf.x()/ratio_x, pointf.y()/ratio_y)


    # 图像坐标映射为像素坐标
    def vertex_map(self):
        if self._leftborder_begin is not None:
            self._leftborder_begin_f = self.point_2_pointf(self._leftborder_begin)
        if self._leftborder_end is not None:
            self._leftborder_end_f = self.point_2_pointf(self._leftborder_end)
        if self._rightborder_begin is not None:
            self._rightborder_begin_f = self.point_2_pointf(self._rightborder_begin)
        if self._rightborder_end is not None:
            self._rightborder_end_f = self.point_2_pointf(self._rightborder_end)
        self._vertex_mapped = True

    def reset(self):
        self._status = Status.DRAW_DONE
        self._leftborder_begin: QPointF = None
        self._leftborder_end: QPointF = None
        self._leftborder_begin_f: QPointF = None
        self._leftborder_end_f: QPointF = None
        self._rightborder_begin: QPointF = None
        self._rightborder_end: QPointF = None
        self._rightborder_begin_f: QPointF = None
        self._rightborder_end_f: QPointF = None
        self._leftborder_done = False
        self._rightborder_done = False


    def setShape(self, shape: DrawShape):
        self._shape = shape

    def setDrawing(self, is_drawing: bool):
        self._is_drawing = is_drawing

    def resizeEvent(self, event: QResizeEvent):
        #print('resize event')
        # 缩放图片
        #Qt.KeepAspectRatio, Qt.IgnoreAspectRatio
        #print('in resize event, size:', self.size())
        if self._pixmap is not None:
            self._pic = self._pixmap.scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
            super(ZImageLabel, self).setPixmap(self._pic)

        self._vertex_mapped = False
        super(ZImageLabel, self).resizeEvent(event)

    def paintEvent(self, event):
        #print('paint event')
        # 先绘制widget本身（图片）
        super(ZImageLabel, self).paintEvent(event)
        #第一次paint要做映射
        if not self._vertex_mapped and self._pixmap is not None:
            #print(self._leftborder_begin, self._leftborder_end, self._leftborder_begin, self._leftborder_end)
            self.vertex_map()

        painter = QPainter(self)
        painter.setPen(QPen(Qt.red, 2))

        if self._status == Status.DRAW_MOVE:
            painter.drawLine(QPoint(self._mx, self._my), QPoint(self._x_begin, self._y_begin))

        if self._leftborder_done and self._leftborder_begin_f is not None and self._leftborder_end_f is not None:
            painter.drawLine(self._leftborder_begin_f, self._leftborder_end_f)

        if self._rightborder_done and self._rightborder_begin_f is not None and self._rightborder_end_f is not None:
            painter.drawLine(self._rightborder_begin_f, self._rightborder_end_f)



    def mouseMoveEvent(self, event: QMouseEvent):
        if self._pixmap is None:
            return
        if self._status == Status.DRAW_BEGIN:
            self._mx = event.pos().x()
            self._my = event.pos().y()
            self._status = Status.DRAW_MOVE
            self.update()
        elif self._status == Status.DRAW_MOVE:
            self._mx = event.pos().x()
            self._my = event.pos().y()
            self.update()

    def mousePressEvent(self, event: QMouseEvent):

        if self._pixmap is None:
            return
        if event.button() != Qt.MouseButton.LeftButton:
            return
        #左边界和右边界都已经画好
        if self._leftborder_done and self._rightborder_done:
            return
        #左边界已经画好，仍然想画左边界
        if self._leftborder_done and self._shape == DrawShape.LEFT_BORDER:
            return
        #右边界已经画好，仍然想画右边界
        if self._rightborder_done and self._shape == DrawShape.RIGHT_BORDER:
            return

        self._status = Status.DRAW_BEGIN
        self._x_begin = event.pos().x()
        self._y_begin = event.pos().y()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if self._pixmap is None:
            return
        if event.button() != Qt.MouseButton.LeftButton:
            return
        if self._status != Status.DRAW_MOVE:
            return
        self._status = Status.DRAW_DONE
        self._mx = event.pos().x()
        self._my = event.pos().y()
        if self._shape  == DrawShape.LEFT_BORDER:
            self._leftborder_done = True
            self._leftborder_begin_f = QPointF(self._x_begin, self._y_begin)
            self._leftborder_end_f   = QPointF(self._mx, self._my)
            self._leftborder_begin   = self.pointf_2_point(self._leftborder_begin_f)
            self._leftborder_end     = self.pointf_2_point(self._leftborder_end_f)
            self.borderDrewSig.emit(True, self.getLeftBorder())

        if self._shape  == DrawShape.RIGHT_BORDER:
            self._rightborder_done = True
            self._rightborder_begin_f = QPointF(self._x_begin, self._y_begin)
            self._rightborder_end_f   = QPointF(self._mx, self._my)
            self._rightborder_begin   = self.pointf_2_point(self._rightborder_begin_f)
            self._rightborder_end     = self.pointf_2_point(self._rightborder_end_f)
            self.borderDrewSig.emit(False, self.getRightBorder())

    #双击鼠标右键：清除左边界和右边界
    def mouseDoubleClickEvent(self, event: QMouseEvent):
        #print('double clicked')
        if self._pixmap is None:
            return
        if event.button() != Qt.MouseButton.RightButton:
            return
        #print('will reset')
        self.reset()
        self.borderClearSig.emit()
        self.update()

    def setPixmapT(self, pixmap: QPixmap):
        self._pixmap = pixmap
        #self._pic = self._pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self._pic = self._pixmap.scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        self._pic = pixmap
        super(ZImageLabel, self).setPixmap(self._pic)
        self.update()

    def setLeftBorder(self, line):
        self._leftborder_begin = QPointF(line[0][0], line[0][1])
        self._leftborder_end   = QPointF(line[1][0], line[1][1])
        self._leftborder_done = True

    def setRightBorder(self, line):
        self._rightborder_begin = QPointF(line[0][0], line[0][1])
        self._rightborder_end = QPointF(line[1][0], line[1][1])
        self._rightborder_done = True

    def getLeftBorder(self):
        return [[int(self._leftborder_begin.x()), int(self._leftborder_begin.y())],
                [int(self._leftborder_end.x()), int(self._leftborder_end.y())]]

    def getRightBorder(self):
        return [[int(self._rightborder_begin.x()), int(self._rightborder_begin.y())],
                [int(self._rightborder_end.x()), int(self._rightborder_end.y())]]