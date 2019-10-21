from Maintenance_main import Sens
from datetime import datetime
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import QTimer, Qt
from Weather_design import Ui_Frame
import sys


class Weather_main(QtWidgets.QFrame):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Frame()
        self.ui.setupUi(self)
        self.cline = self.ui.cl1
        self.w1line = self.ui.wt1
        self.w2line = self.ui.wt2
        self.l_time = self.ui.l_time
        self.tik = True
        self.red = "background-color: qconicalgradient(cx:1, cy:0.329773, \
                    angle:0, stop:0.3125 rgba(239, 0, 0, 255), stop:1 rgba(255, 255, 255, 255));"
        self.green = "background-color: qconicalgradient(cx:1, cy:0.529, angle:0,\
                    stop:0.215909 rgba(38, 174, 23, 255), stop:1 rgba(255, 255, 255, 255));"
        self.yellow = "background-color: qconicalgradient(cx:1, cy:0.329773, \
                    angle:0, stop:0.363636 rgba(219, 219, 0, 255), stop:1 rgba(255, 255, 255, 255));"
        self.wSett()

    def wSett(self):
        with open('wconf.ini', 'r', encoding='utf-8') as f:
            self.iram = f.readline().strip()[8:]
            self.cl = f.readline().strip()[8:]
            self.wt1 = f.readline().strip()[8:]
            self.wt2 = f.readline().strip()[8:]
            self.wRun()
            self.wTime()

    def wRun(self):
        wt = [self.wt1, self.wt2]
        wline = [self.w1line, self.w2line]
        for i in range(0, 2):
            self.wt = wt[i]
            self.wline = wline[i]
            s = Sens(self.iram, "", self.cl, self.wt, '1', '0', '0')
            s.wtInit()
            s.clInit()
            self.wline.setText(s.wt_val)
            self.cline.setText(s.cl_val)
            if s.cl_error == 1:
                self.cline.setStyleSheet(self.red)
            elif s.cl_error == 2:
                self.cline.setStyleSheet(self.yellow)
            elif s.cl_error == 3:
                self.cline.setStyleSheet(self.red)
                self.cline.setText("Нет файла")
            else:
                self.cline.setStyleSheet(self.green)
            if s.wt_error == 1:
                self.wline.setStyleSheet(self.red)
            elif s.wt_error == 2:
                self.wline.setStyleSheet(self.yellow)
            elif s.wt_error == 3:
                self.wline.setStyleSheet(self.red)
                self.wline.setText("Нет файла")
            else:
                self.wline.setStyleSheet(self.green)

        QTimer.singleShot(3000, self.wRun)

    def wTime(self):
        t = datetime.strftime(datetime.now(), " %d-%m-%y  %H:%M:%S")
        self.l_time.setText(t)
        if self.tik == True:
            self.l_time.setStyleSheet(self.green)
            self.tik = False
        else:
            self.l_time.setStyleSheet("background-color: ")
            self.tik = True
        QTimer.singleShot(1000, self.wTime)
    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    application = Weather_main()
    application.show()
    sys.exit(app.exec_())
