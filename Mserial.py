import time, sys, os, serial, threading, multiprocessing
from winreg import *
from datetime import datetime as tm
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from Mserial_design import Ui_MainWindow as ComView
from PortSettings_design import Ui_Frame as Settings


class SerialSett(QtWidgets.QFrame):
    def __init__(self):
        super().__init__()
        self._wdw = Settings()
        self._wdw.setupUi(self)
        self._wdw.addButton.clicked.connect(self.settWrite)
        self._wdw.applyButton.clicked.connect(self.applySett)
        self._wdw.extButton.clicked.connect(self.close)
        self._wdw.comBox.currentTextChanged.connect(self.settShow)
        self.com_list = [
            'COM01', 'COM02', 'COM03', 'COM04', 'COM05', 'COM06', 'COM07', 'COM08',
            'COM09', 'COM10', 'COM11', 'COM12', 'COM13', 'COM14', 'COM15', 'COM16',
            'COM17', 'COM18', 'COM19', 'COM20', 'COM21', 'COM22', 'COM23', 'COM24',
            'COM25', 'COM26', 'COM27', 'COM28', 'COM29', 'COM30', 'COM31', 'COM32'
        ]
        self.sens_types = ['LT', 'CL', 'WT', 'MAWS', 'MILOS', 'PTB']
        self.baud_list = ['300', '600', '1200', '1800', '2400', '4800', '7200', '9600']
        self.byte_list = ['5', '6', '7', '8']
        self.par_list = ['NO', 'ODD', 'EVEN', 'MARK', 'SPACE']
        self.sbit_list = ['1', '1.5', '2']
        self.sens_dic = {}
        self.types_dic = {}
        self.baud_dic = {}
        self.byte_dic = {}
        self.par_dic = {}
        self.sbit_dic = {}
        self.arh_dic = {}
        self._wdw.comBox.addItems(['None'] + self.com_list)
        self._wdw.typesBox.addItems([''] + self.sens_types)
        self._wdw.baudBox.addItems([''] + self.baud_list)
        self._wdw.bytesizeBox.addItems([''] + self.byte_list)
        self._wdw.parityBox.addItems([''] + self.par_list)
        self._wdw.stopbitsBox.addItems([''] + self.sbit_list)
        self.settRead()

    def settRead(self):
        aReg = ConnectRegistry(None, HKEY_CURRENT_USER)
        serKey = f"Software\\IRAM\\MAINT\\SERIAL\\"
        # Читаем настройки программы
        try:
            rKey = OpenKey(aReg, r"Software\IRAM\MAINT\PROGSETT")
            self.station = QueryValueEx(rKey, 'STATION')[0]
            # Читаем настройки СОМ портов
            for i in self.com_list:
                rKey = OpenKey(aReg, serKey+i)
                sens_key = 'SENSNAME'
                types_key ='SENSTYPE'
                baud_key = 'BAUDRATE'
                byte_key = 'BYTESIZE'
                par_key = 'PARITY'
                sbit_key = 'STOPBITS'
                arh_key = 'SENSARH'
                try:
                    sens_val = QueryValueEx(rKey, sens_key)[0]
                    if sens_val == 'None':
                        pass
                    else:
                        types_val = QueryValueEx(rKey, types_key)[0]
                        baud_val = QueryValueEx(rKey, baud_key)[0]
                        byte_val = QueryValueEx(rKey, byte_key)[0]
                        par_val = QueryValueEx(rKey, par_key)[0]
                        sbit_val = QueryValueEx(rKey, sbit_key)[0]
                        arh_val = QueryValueEx(rKey, arh_key)[0]
                        self.sens_dic[i] = sens_val
                        self.types_dic[i] = types_val
                        self.baud_dic[i] = baud_val
                        self.byte_dic[i] = byte_val
                        self.par_dic[i] = par_val
                        self.sbit_dic[i] = sbit_val
                        self.arh_dic[i] = int(arh_val)
                except WindowsError as e:
                    keys = dict.fromkeys([sens_key, types_key, baud_key,
                                          byte_key, par_key, sbit_key, arh_key])
                    nKey = CreateKeyEx(aReg, serKey+i, 0, KEY_ALL_ACCESS)
                    for k, v in keys.items():
                        SetValueEx(nKey, k, 0, REG_SZ, str(v))
            self.textShow()
        except WindowsError as e:
            for i in self.com_list:
                CreateKeyEx(aReg, serKey+i, 0, KEY_ALL_ACCESS)
            self.settRead()

    def settShow(self, value):
        # При выборе сом порта выставляем настройки
        if value == 'None':
            pass
        else:
            try:
                sens_val = self.sens_dic[value]
                types_val = self.types_dic[value]
                baud_val = self.baud_dic[value]
                byte_val = self.byte_dic[value]
                par_val = self.par_dic[value]
                sbit_val = self.sbit_dic[value]
                arh_val = self.arh_dic[value]
                self._wdw.sensEdit.setText(sens_val)
                self._wdw.typesBox.setCurrentText(types_val)
                self._wdw.baudBox.setCurrentText(baud_val)
                self._wdw.bytesizeBox.setCurrentText(byte_val)
                self._wdw.parityBox.setCurrentText(par_val)
                self._wdw.stopbitsBox.setCurrentText(sbit_val)
                self._wdw.arh_sensCh.setChecked(arh_val)
            except Exception as e:
                pass

    def textShow(self):
        # Выводим данные в таблицу
        self._wdw.comText.clear()
        self._wdw.baudText.clear()
        self._wdw.byteText.clear()
        self._wdw.parityText.clear()
        self._wdw.sbitText.clear()
        self._wdw.typesText.clear()
        self._wdw.sensText.clear()
        for com, sens in self.sens_dic.items():
            if not sens:
                pass
            else:
                self._wdw.comText.append(com)
                self._wdw.sensText.append(sens)
                types_val = self.types_dic[com]
                self._wdw.typesText.append(types_val)
                baud_val = self.baud_dic[com]
                self._wdw.baudText.append(baud_val)
                byte_val = self.byte_dic[com]
                self._wdw.byteText.append(byte_val)
                par_val = self.par_dic[com]
                self._wdw.parityText.append(par_val)
                sbit_val = self.sbit_dic[com]
                self._wdw.sbitText.append(sbit_val)

    def settWrite(self):
        com = self._wdw.comBox.currentText()
        sens_val = self._wdw.sensEdit.text()
        types_val = self._wdw.typesBox.currentText()
        baud_val = self._wdw.baudBox.currentText()
        byte_val = self._wdw.bytesizeBox.currentText()
        par_val = self._wdw.parityBox.currentText()
        sbit_val = self._wdw.stopbitsBox.currentText()
        arh_val = str(int(self._wdw.arh_sensCh.isChecked()))
        sens_key = 'SENSNAME'
        types_key = 'SENSTYPE'
        baud_key = 'BAUDRATE'
        byte_key = 'BYTESIZE'
        par_key = 'PARITY'
        sbit_key = 'STOPBITS'
        arh_key = 'SENSARH'
        if com == 'None':
            pass
        else:
            aReg = ConnectRegistry(None, HKEY_CURRENT_USER)
            try:
                nKey = CreateKeyEx(aReg, f"Software\\IRAM\\MAINT\\SERIAL\\{com}", 0, KEY_ALL_ACCESS)
                SetValueEx(nKey, sens_key, 0, REG_SZ, sens_val)
                SetValueEx(nKey, types_key, 0, REG_SZ, types_val)
                SetValueEx(nKey, baud_key, 0, REG_SZ, baud_val)
                SetValueEx(nKey, byte_key, 0, REG_SZ, byte_val)
                SetValueEx(nKey, par_key, 0, REG_SZ, par_val)
                SetValueEx(nKey, sbit_key, 0, REG_SZ, sbit_val)
                SetValueEx(nKey, arh_key, 0, REG_SZ, arh_val)
            except Exception:
                pass
            self.settRead()

    def applySett(self):
        self.close()
        window.show()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()


class SerialWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.ui = ComView()
        self.ui.setupUi(self)
        self.comBx1 = self.ui.comBox1
        self.comBx2 = self.ui.comBox2
        self.comBx3 = self.ui.comBox3
        self.comBx4 = self.ui.comBox4
        self.comBr1 = self.ui.comBrowser1
        self.comBr2 = self.ui.comBrowser2
        self.comBr3 = self.ui.comBrowser3
        self.comBr4 = self.ui.comBrowser4
        self.senBt1 = self.ui.sensButton1
        self.senBt2 = self.ui.sensButton2
        self.senBt3 = self.ui.sensButton3
        self.senBt4 = self.ui.sensButton4
        self.statText = self.ui.statBrowser
        self.startBt = self.ui.startButton
        self.startBt.clicked.connect(self.portStart)
        self.ui.actSettings.triggered.connect(self.settInit)
        self.senBt1.clicked.connect(lambda: self.comBr1.setText(' '))
        self.senBt2.clicked.connect(lambda: self.comBr2.setText(' '))
        self.senBt3.clicked.connect(lambda: self.comBr3.setText(' '))
        self.senBt4.clicked.connect(lambda: self.comBr4.setText(' '))
        # Активируем Shortcuts
        self.settShct = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+S"), self)
        self.settShct.activated.connect(self.settInit)
        self.runShct = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+R"), self)
        self.runShct.activated.connect(self.portStart)
        # Берем настройки из SerialSett
        self._sett = SerialSett()
        # Заполняем боксы наименованиеми портов
        self.port_list = ['None']
        for com, sens in self._sett.sens_dic.items():
            if not sens:
                pass
            else:
                self.port_list += [com]
        self.comBx1.addItems(self.port_list)
        self.comBx2.addItems(self.port_list)
        self.comBx3.addItems(self.port_list)
        self.comBx4.addItems(self.port_list)
        # Start port reading
        self.threads_stop = None
        self.portStart()

    def threadPorts(self):
        self.threads_stop = False
        # Запуск потоков подключенных портов
        try:
            for com, sens in self._sett.sens_dic.items():
                if not sens:
                    pass
                else:
                    port_args = [
                        com,
                        self._sett.baud_dic[com],  # baud
                        self._sett.byte_dic[com],  # byte
                        self._sett.par_dic[com],  # parity
                        self._sett.sbit_dic[com],  # stop bit
                        sens,  # sens
                        self._sett.types_dic[com],  # types
                        self._sett.arh_dic[com]    # if arh write
                    ]
                    t = threading.Thread(target=self.comListen, args=(port_args),
                                              daemon=True)
                    t.start()
        except Exception as e:
            self.logWrite(f'threadPorts {e}')
            pass

    def comListen(self, *port_args):
        # Считывание данных с СОМ портов, вывод в файл и на Ui
        try:
            # Настройки СОМ порта
            if port_args[3] == 'EVEN':
                parity = serial.PARITY_EVEN
            elif port_args[3] == 'ODD':
                parity = serial.PARITY_ODD
            elif port_args[3] == 'NO':
                parity = serial.PARITY_NONE
            elif port_args[3] == 'MARK':
                parity = serial.PARITY_MARK
            elif port_args[3] == 'SPACE':
                parity = serial.PARITY_SPACE
            else:
                parity = 'NO'
            comport = port_args[0]
            if comport[3::2] == "0":
                comport = (comport[:3] + comport[4:5])
            ser = serial.Serial(
                port=comport,
                baudrate=port_args[1],
                bytesize=int(port_args[2]),
                parity=parity,
                stopbits=int(port_args[4]),
                timeout=3,
            )
            while not self.threads_stop:
                # Запуск считывания сом порта
                try:
                    if port_args[6] == 'CL':
                        buf = ser.read_until('\r').rstrip()
                    elif port_args[6] == 'LT':
                        b = ser.readline()
                        buf = b + ser.read_until('\r').rstrip()
                    elif port_args[6] == 'MILOS':
                        buf = ser.readline().strip()
                    else:
                        buf = ser.readline().rstrip()
                    data = buf.decode('utf-8')
                except Exception as e:
                    self.logWrite(f'comListen_0 {e}')
                if not data:
                    pass
                else:
                    text = [data, port_args[0], port_args[5], port_args[6]]
                    # Инициализация записи в файл и вывод на gui
                    self.thread.getData(text)
                    self.dataSort(text)
                    if port_args[7]:
                        self.writeArh(text)
                time.sleep(1)
        except Exception as e:
            self.logWrite(f'comListen_1 {e}')

    def dataSort(self, text):
        try:
            data = text[0]
            com = text[1]
            sens = text[2]
            types = text[3]
            timeNow = tm.now().strftime("%H:%M:%S %d-%m-%Y  ")
            if types == 'WT':
                if 'WIMWV' in data:
                    buf = data.split(',')
                    data = timeNow + com + ' ' + str(buf[1]) + ' ' + str(buf[3])
                    self.dataWrite(sens, data)
                elif 'TU' in data:
                    data = timeNow + '\n' + data
                    self.dataWrite(com + '_TU', data)
            if types == 'MAWS':
                if 'PAMWV' in data:
                    buf = data.split(',')
                    data = timeNow + com + ' ' + str(buf[1]) + ' ' + str(buf[3])
                    self.dataWrite(sens, data)
                elif 'TU' in data:
                    data = timeNow + '\n' + data
                    self.dataWrite(com + '_TU', data)
            if types == 'MILOS':
                if 'A' in data:
                    pos = data.index('A')
                    if pos <= 1:
                        buf = data[pos:]
                        if len(buf) == 6:
                            vd = buf[1:]
                            v = int(vd[:3]) / 10
                            d = int(vd[3:]) * 4.66
                            data = timeNow + com + ' ' + str(d) + ' ' + str(v)
                            self.dataWrite(sens, data)
                elif 'TU' in data:
                    buf = data[4:].split()
                    buf.insert(0, 'TU')
                    data = ','.join(buf).replace(',', ' ')
                    data = timeNow + '\n' + data
                    self.dataWrite(com + '_TU', data)
                elif 'P' in data:
                    data = timeNow + '\n' + data
                    self.dataWrite(com + '_P', data)
            if types == 'LT':
                if 'LT' in data and 'VIS' in data:
                    data = timeNow + '\n' + data
                    self.dataWrite(sens, data)
            if types == 'CL':
                if 'CT' in data:
                    data = timeNow + '\n' + data
                    self.dataWrite(sens, data)
            if types == 'PTB':
                if 'PTB' in data:
                    data = timeNow + '\n' + data
                    self.dataWrite(sens, data)
        except Exception as e:
            self.logWrite(f'dataSort {e}')

    def dataWrite(self, sens, data):
        # Запись отсортированных данных с портов в файл
        try:
            if not os.path.exists('Serial'):
                os.mkdir('Serial')
            with open('Serial\\' + sens + '.dat', 'w', encoding='ANSI') as f_sens:
                f_sens.write(data)
        except Exception as e:
            self.logWrite(f'dataWrite {e}')

    def writeArh(self, text):
        # Запись данных с портов в файл
        try:
            data = text[0]
            com = text[1]
            sens = text[2]
            # types = text[3]
            timeNow = tm.now().strftime("%H:%M:%S %d-%m-%Y  ")
            if not os.path.exists('Arh_Sens'):
                os.mkdir('Arh_Sens')
            with open('Arh_Sens\\' + com + '.dat', 'a') as f_com:
                f_com.write(f"{timeNow} ** {sens}\n{data}\n")
        except Exception as e:
            self.logWrite(f'writeArh {e}')

    def textSend(self, text):
        try:
            data = text[0]
            com = text[1]
            sens = text[2]
            # Отображение текста на Ui
            self.statText.setText(data)
            com1 = self.comBx1.currentText()
            com2 = self.comBx2.currentText()
            com3 = self.comBx3.currentText()
            com4 = self.comBx4.currentText()
            if com1 == com:
                self.comBr1.append(data)
                self.senBt1.setText(sens)
            elif com2 == com:
                self.comBr2.append(data)
                self.senBt2.setText(sens)
            elif com3 == com:
                self.comBr3.append(data)
                self.senBt3.setText(sens)
            elif com4 == com:
                self.comBr4.append(data)
                self.senBt4.setText(sens)
            if com1 == 'None':
                self.comBr1.setText(' ')
                self.senBt1.setText(' ')
            if com2 == 'None':
                self.comBr2.setText(' ')
                self.senBt2.setText(' ')
            if com3 == 'None':
                self.comBr3.setText(' ')
                self.senBt3.setText(' ')
            if com4 == 'None':
                self.comBr4.setText(' ')
                self.senBt4.setText(' ')
        except Exception as e:
            self.logWrite(f'textSend {e}  {text}')
            pass

    def portStart(self):
        try:
            self.startBt.disconnect()
            self.startBt.setText('STOP')
            self.startBt.clicked.connect(self.portStop)
            self.threadPorts()
            self.thread = Thread1()
            self.thread.slot.connect(self.textSend)
            self.thread.start()
        except Exception as e:
            self.logWrite(f'portStart {e}')

    def portStop(self):
        try:
            self.threads_stop = True
            self.startBt.disconnect()
            self.startBt.setText('START')
            self.startBt.clicked.connect(self.portStart)
        except Exception as e:
            self.logWrite(f'portStop {e}')

    def settInit(self):
        self.close()
        self._sett.show()

    def logWrite(self, log):
        if not os.path.exists('LOGs'):
            os.mkdir('LOGs')
        t = tm.now().strftime("%d-%m-%y %H:%M:%S")
        with open(r'LOGs\serLog.txt', 'a', encoding='utf-8') as f_rep:
            f_rep.write(t + " " + log + "\n")

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()


class Thread1(QThread):
    slot = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.text = "Thread start"

    def run(self):
        if self.text != "Thread start":
            self.slot.emit(self.text)

    def getData(self, data):
        self.text = data
        self.run()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = SerialWindow()
    window.show()
    sys.exit(app.exec_())
