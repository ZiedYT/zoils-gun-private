
import sys, time, webbrowser
import serial.tools.list_ports
import os
import json
from PyQt5.QtWidgets import QApplication,QTabWidget,QDoubleSpinBox, QDialog, QMainWindow, QSystemTrayIcon, QMenu, QAction, QCheckBox, QComboBox, QSpinBox, QLineEdit, QHBoxLayout, QPushButton, QLabel, QMessageBox
from PyQt5 import QtCore, uic
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QThread, QEvent, QTimer
# from twitchSocket import Socket
from streamelements import StreamElementsClient
from arduino import arduino

import ctypes
print("Starting....")
exename = sys.argv[0]

def hideConsole():
    """
    Hides the console window in GUI mode. Necessary for frozen application, because
    this application support both, command line processing AND GUI mode and theirfor
    cannot be run via pythonw.exe.
    """

    whnd = ctypes.windll.kernel32.GetConsoleWindow()
    if whnd != 0:
        ctypes.windll.user32.ShowWindow(whnd, 0)
        # if you wanted to close the handles...
        #ctypes.windll.kernel32.CloseHandle(whnd)

def showConsole():
    """Unhides console window"""
    whnd = ctypes.windll.kernel32.GetConsoleWindow()
    if whnd != 0:
        ctypes.windll.user32.ShowWindow(whnd, 1)
if(not "_console.exe" in exename):
    hideConsole()

class MainWindow(QMainWindow):
    def __init__(self , app ):
        super().__init__()
        self.lastCreds = 0
        self.data={}
        self.ports=[]
        self.arduino=None
        self.save_folder = os.path.join(os.getenv('APPDATA'), 'zoilgun')
        if(not os.path.isdir(self.save_folder)):
            os.mkdir(self.save_folder)

        self.initialize()
        self.connect()
        self.loadJson()

        self.start_listener()
        self.timer = QTimer()
        self.timer.timeout.connect(self.spin)
        self.timer.start(100)

    def initialize(self):
        uic.loadUi('main.ui', self)
        self.setWindowTitle("Zoil's Big Black Gun, by ZiedYT")        
        import ctypes
        myappid = 'zoilgun'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        self.show()
        self.connect_menu()
        self.setWindowIcon(QIcon('icon.png'))
        self.setMaximumWidth(self.width())
        self.setMaximumHeight(self.height())
        self.setMinimumWidth(self.width())
        self.setMinimumHeight(self.height())
        
    def connect_menu(self):
        self.menu = QMenu()
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon('icon.png'))
        self.tray_icon.setToolTip("Zoil's Gun")
        self.tray_icon.setContextMenu(self.menu)
        self.tray_icon.show()
        self.show_action = QAction('Show', self)
        self.show_action.triggered.connect(self.maximise)
        self.menu.addAction(self.show_action)
        self.quit_action = QAction('Quit', self)
        self.quit_action.triggered.connect(self.quit)
        self.menu.addAction(self.quit_action)

    def maximise(self):
        self.setWindowFlags(QtCore.Qt.Window)
        self.show()
        self.setWindowState(QtCore.Qt.WindowMaximized)
        self.move(self.loc.x(), self.loc.y())

    def changeEvent(self, event):
        if event.type() == QEvent.WindowStateChange:
            if self.windowState() & QtCore.Qt.WindowMinimized:            
                self.loc = self.geometry()
                self.setWindowFlags(QtCore.Qt.Tool)
                return 
            
    def loadJson(self):
        jsonpath = os.path.join(self.save_folder,"data.json")
        self.data["bits"]={}
        self.data["gifted"]={}
        self.data["subs"]={}

        if(not os.path.isfile(jsonpath)):
            return
        
        tempdata={}
        with open(jsonpath) as json_file:
            tempdata=json.load(json_file)    

        # tempdata = json.load(jsonpath) 
        # self.data["channel_name"] = tempdata.get("channel_name","")
        self.data["token"] = tempdata.get("token","")
        # self.lineEdit_channelname.setText(self.data["channel_name"] )
        self.lineEdit_token.setText(self.data["token"])
        self.checkBox_active.setChecked(tempdata.get("active",False) )
        self.doubleSpinBox_duration.setValue(tempdata.get("duration",0.5))
        self.currport = tempdata.get("port","")
        # self.updatePorts()

        self.checkBox_bits.setChecked( tempdata.get("bits",{}).get("use",False) )
        self.spinBox_amountbits.setValue(tempdata.get("bits",{}).get("amount",100) )
        self.checkBox_mutiplebits.setChecked( tempdata.get("bits",{}).get("multi",False) )

        self.checkBox_gifted.setChecked( tempdata.get("gifted",{}).get("use",False) )
        self.spinBox_amountgifted.setValue(tempdata.get("gifted",{}).get("amount",100) )
        self.checkBox_mutiplegifted.setChecked( tempdata.get("gifted",{}).get("multi",False) )

        self.checkBox_subs.setChecked(tempdata.get("subs",{}).get("use",False))

    def saveJson(self):
        
        self.data["port"] = self.comboBox_port.currentText()
        self.data["active"] = self.checkBox_active.isChecked()        
        self.data["duration"] = self.doubleSpinBox_duration.value()

        self.data["bits"]["use"] = self.checkBox_bits.isChecked()
        self.data["bits"]["multi"] = self.checkBox_mutiplebits.isChecked()
        self.data["bits"]["amount"] = self.spinBox_amountbits.value()

        self.data["gifted"]["use"] = self.checkBox_gifted.isChecked()
        self.data["gifted"]["multi"] = self.checkBox_mutiplegifted.isChecked()
        self.data["gifted"]["amount"] = self.spinBox_amountgifted.value()

        self.data["subs"]["use"] = self.checkBox_subs.isChecked()

        file = os.path.join(self.save_folder, 'data.json')
        with open(file, 'w') as outfile:
            json.dump(self.data, outfile)

    def connect(self):
        self.pushButton_token: QPushButton = self.findChild(QPushButton, "pushButton_token")
        self.tokenLink= "https://streamelements.com/dashboard/account/channels"
        self.pushButton_token.clicked.connect( lambda: webbrowser.open(self.tokenLink) )
        # self.lineEdit_channelname: QLineEdit = self.findChild(QLineEdit, "lineEdit_channelname")
        self.lineEdit_token: QLineEdit = self.findChild(QLineEdit,"lineEdit_token")
        self.checkBox_active: QCheckBox = self.findChild(QCheckBox, "checkBox_active")
        self.checkBox_gifted: QCheckBox = self.findChild(QCheckBox,"checkBox_gifted")
        self.checkBox_subs: QCheckBox = self.findChild(QCheckBox,"checkBox_subs")
        self.checkBox_bits: QCheckBox = self.findChild(QCheckBox,"checkBox_bits")
        self.checkBox_mutiplegifted: QCheckBox = self.findChild(QCheckBox,"checkBox_mutiplegifted")
        self.checkBox_mutiplebits: QCheckBox = self.findChild(QCheckBox,"checkBox_mutiplebits")
        self.spinBox_amountgifted:QSpinBox = self.findChild(QSpinBox,"spinBox_amountgifted")
        self.spinBox_amountbits:QSpinBox = self.findChild(QSpinBox,"spinBox_amountbits")
        self.comboBox_port:QComboBox = self.findChild(QComboBox,"comboBox_port")
        self.doubleSpinBox_duration:QDoubleSpinBox = self.findChild(QDoubleSpinBox,"doubleSpinBox_duration")
        self.doubleSpinBox_duration.valueChanged.connect(self.updateDuration)
        self.pushButton_manual:QPushButton=self.findChild(QPushButton,"pushButton_manual")
        self.pushButton_manual.clicked.connect(self.manualBullet)
        self.pushButton_connect:QPushButton=self.findChild(QPushButton,"pushButton_connect")
        self.pushButton_connect.clicked.connect(self.connectESP)


    def connectESP(self):
        if(self.arduino!=None):
            indx= self.comboBox_port.currentIndex()
            res = self.arduino.changePort(self.port_names[indx] )            
            if(res):
                self.pushButton_connect.setText("Connected")
            else:
                self.pushButton_connect.setText("Connect")

    def updatePorts(self):
        ports = list(serial.tools.list_ports.comports())
        if(ports!=self.ports):
            self.currport = self.comboBox_port.currentText()
            self.ports = ports.copy()
            self.comboBox_port.clear()
            self.port_desc = []
            self.port_names= []
            for p in ports:
                self.port_desc.append(p.description)
                self.port_names.append(p.device)

            if(len(self.ports)>0):
                self.comboBox_port.addItems(self.port_desc)
                indx=0
                if(self.currport in self.port_desc):
                    indx = self.port_desc.index(self.currport)
                self.comboBox_port.setCurrentIndex(indx)
                self.currport= self.comboBox_port.currentText()
            else:
                self.currport=""
            
    

    def updateDuration(self):
        if(self.arduino==None):
            return
        self.arduino.duration= self.doubleSpinBox_duration.value()

    def updateCreds(self):
        # channel_name= self.lineEdit_channelname.text()
        token=self.lineEdit_token.text()
        if(token==""):
            return

        self.socket.change(token)
        # self.data["token"] = token

        # # self.socket.updateCredentials(self.data["channel_name"], self.data["token"])
        # if(not self.socket.valid):
        #     self.lineEdit_token.setStyleSheet("border: 3px solid red;")
        # else: 
        #     self.lineEdit_token.setStyleSheet("border: 1px solid black;")

    def onSub(self):
        print("onSub")
        if(not self.checkBox_active.isChecked()):
            return
        if (self.checkBox_subs.isChecked()):
            self.arduino.addQueue()

    def onGifted(self,amount):
        print("onGifted")
        if(not self.checkBox_active.isChecked()):
            return
        if(self.checkBox_gifted.isChecked()):
            mingifts= self.spinBox_amountgifted.value()
            if(amount>=mingifts):
                count = 1 
                if(self.checkBox_mutiplegifted.isChecked()):
                    count = int (amount / mingifts)
                self.arduino.addQueue(count)

    def onBits(self,amount):
        print("onBits")
        if(not self.checkBox_active.isChecked()):
            return
        if(self.checkBox_bits.isChecked()):
            minbits= self.spinBox_amountbits.value()
            if(amount>=minbits):
                count = 1 
                if(self.checkBox_mutiplebits.isChecked()):
                    count = int (amount / minbits)
                self.arduino.addQueue(count)

    def manualBullet(self):
        self.arduino.addQueue()

    def start_listener(self):
        # self.socket = Socket()
        self.socket = StreamElementsClient(self.lineEdit_token.text())
        self.socket.connect() 
        # self.socket.updateCredentials(self.lineEdit_channelname.text(),self.lineEdit_token.text())
        self.qthread = QThread()
        self.socket.moveToThread(self.qthread)

        # self.qthread.started.connect(self.socket.run)
        self.socket.finished.connect(self.qthread.quit)
        self.socket.finished.connect(self.socket.deleteLater)
        self.qthread.finished.connect(self.qthread.deleteLater)
        self.socket.finished.connect(self.quit)

        self.socket.resub.connect(self.onSub)
        self.socket.giftedSubs.connect(self.onGifted)
        self.socket.bits.connect(self.onBits)

        self.qthread.start()

        self.arduino = arduino(port=self.data.get("port",""))
        self.arduino.duration=self.doubleSpinBox_duration.value()


    def spin(self):
        if(time.time() - self.lastCreds > 1):
            self.updateCreds()
            self.updatePorts()
            self.lastCreds=time.time()

    def closeEvent(self, event):
        self.quit()

    def quit(self):
        self.socket.close()
        self.saveJson()
        self.arduino.run_flag=False
        sys.exit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow(app)    
    try:
        sys.exit(app.exec_())
    except Exception as e:
        print(str(e))
        window.quit()
