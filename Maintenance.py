import subprocess, sys, os, time
import psutil
from winreg import *
from pygame import mixer
from datetime import datetime
from datetime import timedelta
from shutil import copyfile as cp
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import QTimer, Qt
from Maintenance_design_manas import Ui_MainWindow as MainWindowManas
from Maintenance_design_osh import Ui_MainWindow as MainWindowOsh
from MaintSettings_design import Ui_Settings
from About_design import Ui_AboutFrame

global ver
ver = '2.0'


class SettingsInit(QtWidgets.QFrame):

    def __init__(self):
        super().__init__()
        self._sett = Ui_Settings()
        self._sett.setupUi(self)
        # Список станций в настройках
        self._sett.stationBx.addItems([' ', 'UCFM', 'UCFO'])
        self.prog_sett_list = [
            'STATION', 'PATH', 'SNDPATH', 'AVPATH', 'DUR',
            'REFRESH', 'REP_W', 'AV_W', 'AV_T1', 'AV_T2', 'SER'
        ]
        self.sens_sett_list = [
            'CLD1', 'CLD2', 'CLD3', 'CLD4', 'VIS1', 'VIS2', 'VIS3',
            'VIS4', 'VIS5', 'VIS6', 'WIND1', 'WIND2', 'WIND3', 'WIND4',
            'WIND5', 'WIND6', 'TEMP1', 'TEMP2', 'PRES1', 'PRES2'
        ]
        self.prog_sett_dic = dict.fromkeys(self.prog_sett_list, '0')
        self.sens_sett_dic = dict.fromkeys(self.sens_sett_list)
        self._sett.stationBx.activated[str].connect(self.stationChange)
        # Привязка кнопок
        self._sett.buttOK.accepted.connect(self.writeSettings)
        self._sett.buttOK.rejected.connect(lambda: self.close())
        self._sett.buttHelp.clicked.connect(self.help)
        self._sett.sens_addBt.clicked.connect(self.addSens)
        self._sett.sound_testBt.clicked.connect(self.sndTest)
        self.readSettings()

    def readSettings(self):
        # Читаем настройки программы
        aReg = ConnectRegistry(None, HKEY_CURRENT_USER)
        try:
            rKey = OpenKey(aReg, r"Software\IRAM\MAINT\PROGSETT")
            for k in self.prog_sett_dic.keys():
                v = QueryValueEx(rKey, k)[0]
                self.prog_sett_dic[k] = v
        except (ValueError, FileNotFoundError)as e:
            Sens.logWrite(self, e)
        self._sett.sens_addBx.addItems([' ', *self.sens_sett_list])
        # Читаем настройки датчиков
        try:
            rKey = OpenKey(aReg, r"Software\IRAM\MAINT\SENSETT")
            for k in self.sens_sett_dic.keys():
                v = QueryValueEx(rKey, k)[0]
                self.sens_sett_dic[k] = v
        except Exception as e:
            Sens.logWrite(self, e)
        # Выводим текст настроек в Settings
        self._sett.stationLb.setText(self.prog_sett_dic['STATION'])
        self._sett.sens_pathLn.setText(self.prog_sett_dic['PATH'])
        self._sett.sound_pathLn.setText(self.prog_sett_dic['SNDPATH'])
        self._sett.f_waitLn.setText(self.prog_sett_dic['DUR'])
        self._sett.refresh_timeLn.setText(self.prog_sett_dic['REFRESH'])
        self._sett.av6_pathLn.setText(self.prog_sett_dic['AVPATH'])
        self._sett.rep_writeCh.setCheckState(int(self.prog_sett_dic['REP_W']))
        self._sett.mserialCh.setCheckState(int(self.prog_sett_dic['SER']))
        self._sett.av6_writeCh.setCheckState(int(self.prog_sett_dic['AV_W']))
        self._sett.av6_time1Ln.setText(self.prog_sett_dic['AV_T1'])
        self._sett.av6_time2Ln.setText(self.prog_sett_dic['AV_T2'])
        self.viewSens()

    # Привязка датчиков
    def addSens(self):
        sens = self._sett.sens_addBx.currentText()
        for k, v in self.sens_sett_dic.items():
            if sens == k:
                v = self._sett.sens_addLn.text()
            else:
                if not v:
                    v = None
            self.sens_sett_dic[k] = v
        self.viewSens()

    # Просмотр привязки датчиков
    def viewSens(self):
        self._sett.sens_viewBr.setText('')
        for k, v in self.sens_sett_dic.items():
            self._sett.sens_viewBr.append(str(k) + '\t ---- \t ' + str(v))

    # Запись настроек в реестр
    def writeSettings(self):
        # Читаем настройки программы из полей для записи в реестр
        self.prog_sett_dic['STATION'] = self._sett.stationLb.text()
        self.prog_sett_dic['PATH'] = self._sett.sens_pathLn.text()
        self.prog_sett_dic['SNDPATH'] = self._sett.sound_pathLn.text()
        self.prog_sett_dic['DUR'] = self._sett.f_waitLn.text()
        self.prog_sett_dic['REFRESH'] = self._sett.refresh_timeLn.text()
        self.prog_sett_dic['AVPATH'] = self._sett.av6_pathLn.text()
        self.prog_sett_dic['REP_W'] = str(self._sett.rep_writeCh.checkState())
        self.prog_sett_dic['SER'] = str(self._sett.mserialCh.checkState())
        self.prog_sett_dic['AV_W'] = str(self._sett.av6_writeCh.checkState())
        self.prog_sett_dic['AV_T1'] = self._sett.av6_time1Ln.text()
        self.prog_sett_dic['AV_T2'] = self._sett.av6_time2Ln.text()
        # Пишем настройки программы в реестр
        aReg = ConnectRegistry(None, HKEY_CURRENT_USER)
        try:
            nKey = CreateKeyEx(aReg, r'Software\IRAM\MAINT\PROGSETT', 0, KEY_ALL_ACCESS)
            for k, v in self.prog_sett_dic.items():
                SetValueEx(nKey, k, 0, REG_SZ, v)
        except Exception as e:
            Sens.logWrite(self, e)
        # Пишем настройки датчиков в реестр
        try:
            nKey = CreateKeyEx(aReg, r'Software\IRAM\MAINT\SENSETT', 0, KEY_ALL_ACCESS)
            for k, v in self.sens_sett_dic.items():
                SetValueEx(nKey, k, 0, REG_SZ, str(v))
        except Exception as e:
            Sens.logWrite(self, e)
        aReg.Close()
        self.goWindow()

    def stationChange(self):
        self.prog_sett_dic['STATION'] = self._sett.stationBx.currentText()
        aReg = ConnectRegistry(None, HKEY_CURRENT_USER)
        nKey = CreateKeyEx(aReg, r'Software\IRAM\MAINT\PROGSETT', 0, KEY_ALL_ACCESS)
        SetValueEx(nKey, 'STATION', 0, REG_SZ, self.prog_sett_dic['STATION'])
        aReg.Close()
        self.readSettings()

    def sndTest(self):
        mixer.init()
        mixer.music.load(self.prog_sett_dic['SNDPATH'])
        mixer.music.play()

    def help(self):
        self.w = QtWidgets.QMainWindow()
        if self.prog_sett_dic['STATION'] == 'UCFM':
            self.win = MainWindowManas()
        else:
            self.win = MainWindowOsh()
        self.win.setupUi(self.w)
        self.w.show()
        self.win.exit.clicked.connect(self.w.close)

    def goWindow(self):
        self.close()
        Window().show()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()


class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self._si = SettingsInit()
        self._si.close()
        self.prog_sett = self._si.prog_sett_dic
        if self.prog_sett['STATION'] == 'UCFM':
            self._wdw = MainWindowManas()
        elif self.prog_sett['STATION'] == 'UCFO':
            self._wdw = MainWindowOsh()
        else:
            self._si.show()
        try:
            self._wdw.setupUi(self)
            self.show()
            self.About = QtWidgets.QFrame()
            self.ui_a = Ui_AboutFrame()
            self.ui_a.setupUi(self.About)
            # Привязка датчиков к окнам и кнопкам
            self.senS = {
                'VIS1': self._wdw.visS1, 'VIS2': self._wdw.visS2, 'VIS3': self._wdw.visS3,
                'VIS4': self._wdw.visS4, 'VIS5': self._wdw.visS5, 'VIS6': self._wdw.visS6,
                'CLD1': self._wdw.cldS1, 'CLD2': self._wdw.cldS2, 'CLD3': self._wdw.cldS3,
                'CLD4': self._wdw.cldS4, 'WIND1': self._wdw.windS1, 'WIND2': self._wdw.windS2,
                'WIND3': self._wdw.windS3, 'WIND4': self._wdw.windS4
            }
            self.senV = {
                'VIS1': self._wdw.visV1, 'VIS2': self._wdw.visV2, 'VIS3': self._wdw.visV3,
                'VIS4': self._wdw.visV4, 'VIS5': self._wdw.visV5, 'VIS6': self._wdw.visV6,
                'CLD1': self._wdw.cldV1, 'CLD2': self._wdw.cldV2, 'CLD3': self._wdw.cldV3,
                'CLD4': self._wdw.cldV4, 'WIND1': self._wdw.windV1, 'WIND2': self._wdw.windV2,
                'WIND3': self._wdw.windV3, 'WIND4': self._wdw.windV4
            }
            self.senLcd = {'TEMP1': self._wdw.tempV1, 'TEMP2': self._wdw.tempV2,
                           'PRES1': self._wdw.presV1, 'PRES2': self._wdw.presV2
            }
            self.senM = {
                'VIS1': self._wdw.visM1, 'VIS2': self._wdw.visM2, 'VIS3': self._wdw.visM3,
                'VIS4': self._wdw.visM4, 'VIS5': self._wdw.visM5, 'VIS6': self._wdw.visM6,
                'CLD1': self._wdw.cldM1, 'CLD2': self._wdw.cldM2, 'CLD3': self._wdw.cldM3,
                'CLD4': self._wdw.cldM4, 'WIND1': self._wdw.windM1, 'WIND2': self._wdw.windM2,
                'WIND3': self._wdw.windM3, 'WIND4': self._wdw.windM4
            }
            if self.prog_sett['STATION'] == 'UCFM':
                self.senS['WIND5'] = self._wdw.windS5
                self.senS['WIND6'] = self._wdw.windS6
                self.senV['WIND5'] = self._wdw.windV5
                self.senV['WIND6'] = self._wdw.windV6
                self.senM['WIND5'] = self._wdw.windM5
                self.senM['WIND6'] = self._wdw.windM6
            # Определение цветов
            self.red = "background-color: qconicalgradient(cx:1, cy:0.329773, \
                        angle:0, stop:0.3125 rgba(239, 0, 0, 255), stop:1 rgba(255, 255, 255, 255));"
            self.green = "background-color: qconicalgradient(cx:1, cy:0.529, angle:0,\
                        stop:0.215909 rgba(38, 174, 23, 255), stop:1 rgba(255, 255, 255, 255));"
            self.yellow = "background-color: qconicalgradient(cx:1, cy:0.329773, \
                        angle:0, stop:0.363636 rgba(219, 219, 0, 255), stop:1 rgba(255, 255, 255, 255));"
            self.blue = "background-color: qconicalgradient(cx:1, cy:0.529, angle:0,\
                        stop:0.215909 rgba(100, 200, 250, 200), stop:1 rgba(255, 255, 255, 255));"
            # Привязка кнопок к putty
            for k, v in self.senS.items():
                self.puttySett(v, k)
            # Версия программы
            self.ui_a.ver.setText('Version' + ver)
            # Привязка элементов МЕНЮ
            self._wdw.iram.triggered.connect(self.goSett)
            self._wdw.report.triggered.connect(self.openRep)
            self._wdw.log.triggered.connect(self.openLog)
            self._wdw.about.triggered.connect(self.About.show)
            # Привязка кнопок
            self._wdw.start.clicked.connect(self.goStart)
            self._wdw.exit.clicked.connect(self.close)
            self._wdw.terminal.clicked.connect(lambda: self.putty(""))
            # Активируем Shortcuts
            self.settShct = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+S"), self)
            self.settShct.activated.connect(self.goSett)
            self.repShct = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+R"), self)
            self.repShct.activated.connect(self.openRep)
            self.logShct = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+L"), self)
            self.logShct.activated.connect(self.openLog)
            self.snd_play = 0
        except Exception as e:
            Sens.logWrite(self, e)

    def goStart(self):
        self.pause = False
        self.lineColor = 1
        self._wdw.start.setText("Пауза")
        self._wdw.start.setStyleSheet("background-color: ")
        self._wdw.start.clicked.disconnect()
        self._wdw.start.clicked.connect(self.statPause)
        # Start Mserial if checked in settings
        if self.prog_sett['SER'] != '0':
            self.prog_sett['PATH'] = os.getcwd() + '\Serial\\'
            self.serInit()
        # заводим часы
        self.dtimeTick()
        # Soundplay monitor
        self.sndplay()
        # Запуск основного процесса
        self.main()

    def statPause(self):
        self.pause = True
        self._wdw.start.setText("Пуск")
        self._wdw.start.setStyleSheet(self.red)
        self._wdw.start.clicked.disconnect()
        self._wdw.start.clicked.connect(self.goStart)

    def main(self):
        if not self.pause:
            try:
                self.snd_play = 0
                for sens in self.senS.keys():
                    prog = self.prog_sett
                    sensor = self._si.sens_sett_dic[sens]
                    if sensor != 'None':
                        status = self.senS[sens]
                        value = self.senV[sens]
                        snd = self.senM[sens]
                        sens_args = {
                            'path': prog['PATH'], 'sensor': sensor, 'dur': prog['DUR'],
                            'rep': prog['REP_W'], 'mute': snd.isChecked()
                        }
                        s = Sens(**sens_args)
                        if sens[:3] == 'VIS':
                            s.ltInit()
                        elif sens[:3] == 'CLD':
                            s.clInit()
                        elif sens[:4] == 'WIND':
                            s.wtInit()
                        status.setText(s.status)
                        value.setText(s.value)
                        if s.error == 1:
                            status.setStyleSheet(self.red)
                            value.setStyleSheet(self.red)
                            if not snd.isChecked():
                                self.snd_play += 1
                        elif s.error == 2:
                            status.setStyleSheet(self.yellow)
                            value.setStyleSheet(self.yellow)
                            if not snd.isChecked():
                                self.snd_play += 1
                        elif s.error == 3:
                            status.setStyleSheet(self.red)
                            value.setStyleSheet(self.red)
                        else:
                            status.setStyleSheet(self.green)
                            value.setStyleSheet(self.green)
                            snd.setChecked(False)
                for lcd in self.senLcd.keys():
                    prog = self.prog_sett
                    sensor = self._si.sens_sett_dic[lcd]
                    if sensor != 'None':
                        value = self.senLcd[lcd]
                        sens_args = {
                            'path': prog['PATH'], 'sensor': sensor, 'dur': prog['DUR'],
                            'rep': prog['REP_W'], 'mute': 0
                        }
                        s = Sens(**sens_args)
                        if lcd[:4] == 'TEMP':
                            s.tempInit()
                        elif lcd[:4] == 'PRES':
                            s.presInit()
                        value.setText(s.value)
                        value.setStyleSheet(self.blue)
            except ValueError as e:
                Sens.logWrite(self, e)
            if self.lineColor == 1:
                self.lineColor -= 1
                self._wdw.infoLn2.setStyleSheet(self.blue)
            elif self.snd_play > 0:
                self.lineColor +=1
                self._wdw.infoLn2.setStyleSheet(self.red)
            else:
                self.lineColor += 1
                self._wdw.infoLn2.setStyleSheet(self.green)
            QTimer.singleShot(int(self.prog_sett['REFRESH']), self.main)

    def sndplay(self):
        if not self.pause:
            if self._wdw.btn.isChecked():
                pass
            elif self.snd_play > 0:
                mixer.init()
                mixer.music.load(self.prog_sett['SNDPATH'])
                mixer.music.play()
        QTimer.singleShot(5000, self.sndplay)

    def dtimeTick(self):
        if not self.pause:
            s = self.prog_sett
            t = datetime.strftime(datetime.now(), "%d-%m-%y  %H:%M:%S")
            av_time = datetime.strftime(datetime.now(), "%M%S")
            if av_time == (s['AV_T1'] + '00') or av_time == (s['AV_T2'] + '00'):
                if s['AV_W'] != "0":
                    path = s['AVPATH']
                    av = Av6(path)
                    self._wdw.infoLn1.setText(av.av6_rep)
            if s['REP_W'] == '2' or s['REP_W'] == '1':
                repW = "Вкл"
            else:
                repW = "Откл"
            if s['AV_W'] == '2' or s['AV_W'] == '1':
                av6W = "Вкл"
                av_info = ("  ( " + s['AVPATH'] + "      " + s['AV_T1'][:2]
                           + " , " + s['AV_T2'][:2] + " мин )")
            else:
                av6W = "Откл"
                av_info = "    "
            if s['SER'] == '2':
                serR = "Вкл"
            else:
                serR = "Откл"
            self._wdw.statusBar.showMessage(
                "Рабочий каталог: " + s['PATH'] + "    Время ожидания файла:  " + str(s['DUR']) + " мин."
                + "    Время обновления:  " + s['REFRESH'][:-3] + " сек." + "    Отчет: " + repW
                + "    AB6:  " + av6W + av_info + "    Mserial  " + serR)
            self._wdw.timedate.setText(t)
            QTimer().singleShot(1000, self.dtimeTick)
        else:
            self._wdw.timedate.clear()

    def puttySett(self, but, sen):
        but.clicked.connect(lambda: self.putty(sen))

    def putty(self, n):
        subprocess.Popen(['putty.exe', '-load', n])

    def openRep(self):
        subprocess.Popen(['notepad.exe', r'LOGs\maintReport.txt'])

    def openLog(self):
        subprocess.Popen(['notepad.exe', r'LOGs\maintLog.txt'])

    def serInit(self):
        if not self.pause:
            proc = 'Mserial.exe' in (p.name() for p in psutil.process_iter())
            if not proc:
                subprocess.Popen('Mserial.exe')
        QTimer.singleShot(3000, self.serInit)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()

    def goSett(self):
        self.statPause()
        self.close()
        SettingsInit().show()


class Sens():

    def __init__(self, *args, **kwargs):
        self.path = kwargs['path']
        self.sens = kwargs['sensor']
        self.dur = int(kwargs['dur'])
        self.rep = kwargs['rep']
        self.mute = kwargs['mute']
        self.LOGs = "0"

    def checkTime(self, f):
        # Check time and write time difference to dift
        now = datetime.now()
        stat = os.stat(f)
        t_f = datetime.fromtimestamp(stat.st_mtime)
        self.dift = now - t_f

    def ltInit(self):
        try:
            # File in DAT_SENS define
            file = (self.path + self.sens + ".DAT")
            # Check time of file
            self.checkTime(file)
            if self.dift > timedelta(minutes=self.dur):
                self.status = str(self.sens + ' Тревога!!! Нет данных!!!')
                self.error = 1
                self.value = "ERROR"
            else:
                # Чтение файла и запись данных в переменные
                with open(file, 'r', encoding='UTF-8', errors='ignore') as f:
                    tek_f = f.read()
                try:
                    stat = tek_f.split()[6]
                    val = tek_f.split()[4]
                    if val != '///////':
                        self.value = str(float(tek_f.split()[4]))[:-2]
                    else:
                        self.value = val
                except ValueError as e:
                    stat = tek_f.split()[6]
                    self.value = tek_f.split()[4]
                    self.logWrite(self.sens + " ValueError " + str(e) + " " + tek_f)
                battery = stat[2]
                # Проверка ошибок и вывод результата
                if battery == '1' and stat[0] == 'I' or battery == '2' and stat[0] == 'I':
                    self.status = str(self.sens + ' Внимание!!! Работа от батареи!!!')
                    self.error = 2
                elif stat[0] == 'I':
                    self.status = str(self.sens + ' Ненормальная ситуация !!! ' + stat)
                    self.error = 1
                elif stat[0] == 'W':
                    self.status = str(self.sens + ' Предупреждение !!! ' + stat)
                    self.error = 1
                elif stat[0] == 'A':
                    self.status = str(self.sens + ' Авария  !!! ' + stat)
                    self.error = 1
                elif stat[0] == 'E':
                    self.status = str(self.sens + ' Ошибка !!! ' + stat)
                    self.error = 1
                elif stat[0] == 'S':
                    self.status = str(self.sens + ' Открыт интерфейс !!! ' + stat)
                    self.error = 1
                else:
                    self.status = str(self.sens + ' OK ' + stat)
                    self.error = 0
            if self.error != 0:
                if not self.mute:
                    self.repWrite(self.status)
        except FileNotFoundError as e:
            self.status = str(self.sens + " Не найден файл с данными!!!")
            self.error = 3
            self.value = "ERROR"
        except PermissionError as e:
            self.status = str(self.sens + " Обработка....")
            self.error = 0
            self.value = "-----"
        except Exception as e:
            self.status = str(self.sens + " Ошибка !!!")
            self.error = 0
            self.value = "-----"

    def clInit(self):
        try:
            # File in DAT_SENS define
            file = (self.path + self.sens + ".DAT")
            # Check time of file
            self.checkTime(file)
            if self.dift > timedelta(minutes=self.dur):
                self.status = str(self.sens + ' Тревога!!! Нет данных!!!')
                self.error = 1
                self.value = "ERROR"
            else:
                # Чтение файла и запись данных в переменные
                with open(file, 'r', encoding='UTF-8', errors='ignore') as f:
                    tek_f = f.read()
                try:
                    stat = tek_f.split()[7]
                    val = tek_f.split()[4]
                    if val != '/////':
                        self.value = str(float(val))[:-2]
                    else:
                        self.value = val
                except ValueError as e:
                    stat = tek_f.split()[7]
                    self.value = tek_f.split()[4]
                    self.logWrite(self.sens + " ValueError " + str(e) + tek_f)
                battery = stat[5::3]
                norm = '0000'
                # Проверка ошибок и вывод результата
                if battery == '4' and stat[:4] == (norm):
                    self.status = str(self.sens + ' Внимание!!! Работа от батареи!!!')
                    self.error = 2
                elif stat[:4] == (norm):
                    self.status = str(self.sens + ' OK ' + stat)
                    self.error = 0
                else:
                    self.status = str(self.sens + ' Внимание!!! СБОЙ!!! ' + stat)
                    self.error = 1
            if self.error != 0:
                if not self.mute:
                    self.repWrite(self.status)
        except FileNotFoundError as e:
            self.status = str(self.sens + " Не найден файл с данными !!!")
            self.error = 3
            self.value = "ERROR"
        except PermissionError as e:
            self.status = str(self.sens + " Обработка....")
            self.error = 0
            self.value = "-----"
        except Exception as e:
            self.status = str(self.sens + " Ошибка !!!")
            self.error = 0
            self.value = "-----"

    def wtInit(self):
        try:
            # File in DAT_SENS define
            file = (self.path + self.sens + ".DAT")
            # Check time of file
            self.checkTime(file)
            if self.dift > timedelta(minutes=self.dur):
                self.status = str(self.sens + ' Тревога!!! Нет данных!!!')
                self.error = 1
                self.value = "ERROR"
            else:
                # Чтение файла и запись данных в переменные
                with open(file, 'r', encoding='UTF-8', errors='ignore') as f:
                    tek_f = f.read()
                try:
                    dd = float(tek_f.split()[3][:3])
                    ff = float(tek_f.split()[4])
                    self.value = (str(dd)[:-2] + " / " + str(ff))
                except ValueError as e:
                    dd = float(tek_f.split()[4][:3])
                    ff = float(tek_f.split()[5])
                    self.value = (str(dd)[:-2] + " / " + str(ff))
                    self.logWrite(self.sens + " ValueError " + str(e) + " " + tek_f)
                stat = "OK"
                # Проверка ошибок и вывод результата
                self.status = (self.sens + " " + stat)
                self.error = 0
            if self.error != 0:
                if not self.mute:
                    self.repWrite(self.status)
        except FileNotFoundError as e:
            self.status = str(self.sens + " Не найден файл с данными !!!")
            self.error = 3
            self.value = "ERROR"
        except PermissionError as e:
            self.status = str(self.sens + " Обработка.... ")
            self.error = 0
            self.value = "-----"
        except Exception as e:
            self.status = str(self.sens + " Ошибка !!!")
            self.error = 0
            self.value = "-----"

    def tempInit(self):
        try:
            # File in DAT_SENS define
            file = (self.path + self.sens + ".DAT")
            # Check time of file
            self.checkTime(file)
            if self.dift > timedelta(minutes=self.dur):
                self.value = "ERROR"
            else:
                with open(file, 'r', encoding='utf-8') as f:
                    self.value = f.read().split()[3]
        except Exception as e:
            self.value = "ERROR"

    def presInit(self):
        try:
            # File in DAT_SENS define
            file = (self.path + self.sens + ".DAT")
            # Check time of file
            self.checkTime(file)
            if self.dift > timedelta(minutes=self.dur):
                self.value = "ERROR"
            else:
                with open(file, 'r', encoding='utf-8') as f:
                    self.value = f.read().split()[3]
        except Exception as e:
            self.value = "ERROR"

    def repWrite(self, r):
        if self.rep != "0":
            try:
                if not os.path.exists('LOGs'):
                    os.mkdir('LOGs')
                t = datetime.strftime(datetime.now(), "%d-%m-%y %H:%M:%S")
                with open(r'LOGs\maintReport.txt', 'a', encoding='utf-8') as f_rep:
                    f_rep.write(t + " " + r + "\n")
            except Exception as e:
                self.LOGs = str(e)

    def logWrite(self, e):
        try:
            if not os.path.exists('LOGs'):
                os.mkdir('LOGs')
            t = datetime.strftime(datetime.now(), "%d-%m-%y %H:%M:%S")
            with open(r'LOGs\maintLog.txt', 'a', encoding='utf-8') as f_bug:
                f_bug.write(t + " " + str(e) + "\n")
        except Exception as e:
            self.LOGs = str(e)


class Av6():

    def __init__(self, path):
        self.arh = path
        self.arhDirDef()

    def arhDirDef(self):
        try:
            self.t = datetime.strftime(datetime.now(), "%d %m %Y %H%M")
            t = self.t.split(' ')
            self.day = ('D' + t[0])
            self.month = ('M' + t[1])
            self.year = ('G' + t[2])
            self.hour = t[3]
            self.arh_src_dir = f'{self.arh}\ARX__AB6\{self.year}\{self.month}\{self.day}'
            self.arh_dst_dir = f'AV6_ARH\{self.year}\{self.month}\{self.day}'
            self.arhCopy()
        except Exception as e:
            Sens.logWrite(self, e)
            self.LOGs = str(e)

    def arhCopy(self):
        try:
            if os.path.exists(self.arh_src_dir):
                if not os.path.exists(self.arh_dst_dir):
                    os.makedirs(self.arh_dst_dir)
                self.arh_src = self.arh_src_dir + '\\' + 'AB6.DAT'
                self.arh_dst = self.arh_dst_dir + '\\' + 'AB6_' + self.hour + '.DAT'
                try:
                    cp(self.arh_src, self.arh_dst)
                    self.av6Rep(self.hour[:2] + ':' + self.hour[2:] + ' Файл АВ-6 успешно записан!')
                except Exception as e:
                    self.av6Rep(self.hour[:2] + ':' + self.hour[2:] + ' Файл АВ-6 не записан!')
                    Sens.logWrite(self, e)
            else:
                self.av6Rep(self.hour[:2] + ':' + self.hour[2:] + ' Исходник АВ-6 не найден!')
        except Exception as e:
            Sens.logWrite(self, e)
            self.LOGs = str(e)

    def av6Rep(self, r):
        self.av6_rep = r
        try:
            if not os.path.exists('LOGs'):
                os.mkdir('LOGs')
            with open(r'LOGs\av6Report.txt', 'a', encoding='utf-8') as f_rep:
                f_rep.write(r + "\n")
        except Exception as e:
            Sens.logWrite(self, e)
            self.LOGs = str(e)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    application = Window()
    sys.exit(app.exec_())
