import cv2
import numpy as np
from PyQt5 import QtCore

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import pyqtgraph as pg
import sys
import time
from compute import Compute
from webcam import Webcam
from video import Video
from interface import waitKey, plotXY

class Communicate(QObject):
    closeApp = pyqtSignal()
    
    
class HRM(QMainWindow, QThread):
    def __init__(UserGUI):
        super(HRM,UserGUI).__init__()
        UserGUI.initUI()
        UserGUI.webcam = Webcam()
        UserGUI.video = Video()
        UserGUI.input = UserGUI.webcam
        UserGUI.dirname = ""
        print("Input: Camera")
        UserGUI.statusBar.showMessage("Input: Camera",5000)
        UserGUI.compute = Compute()
        UserGUI.status = False
        UserGUI.frame = np.zeros((10,10,3),np.uint8)
        UserGUI.bpm = 0
        
    def initUI(UserGUI):
    
        font = QFont()
        font.setPointSize(16)
		
        UserGUI.btnStart = QPushButton("Start", UserGUI)
        UserGUI.btnStart.move(440,520)
        UserGUI.btnStart.setFixedWidth(200)
        UserGUI.btnStart.setFixedHeight(50)
        UserGUI.btnStart.setFont(font)
        UserGUI.btnStart.clicked.connect(UserGUI.run)
        
        UserGUI.cbbInput = QComboBox(UserGUI)
        UserGUI.cbbInput.addItem("Webcam")
        UserGUI.cbbInput.setCurrentIndex(0)
        UserGUI.cbbInput.setFixedWidth(200)
        UserGUI.cbbInput.setFixedHeight(50)
        UserGUI.cbbInput.move(20,520)
        UserGUI.cbbInput.setFont(font)
        UserGUI.cbbInput.activated.connect(UserGUI.selectInput)
        
        UserGUI.lblDisplay = QLabel(UserGUI) 
        UserGUI.lblDisplay.setGeometry(10,10,640,480)
        UserGUI.lblDisplay.setStyleSheet("background-color: #000000")
        
        UserGUI.lblROI = QLabel(UserGUI) 
        UserGUI.lblROI.setGeometry(660,10,200,200)
        UserGUI.lblROI.setStyleSheet("background-color: #000000")
        
        UserGUI.lblHR = QLabel(UserGUI) 
        UserGUI.lblHR.setGeometry(900,20,300,40)
        UserGUI.lblHR.setFont(font)
        UserGUI.lblHR.setText("Frequency: 0 Hz")
        
        UserGUI.lblHR2 = QLabel(UserGUI) 
        UserGUI.lblHR2.setGeometry(900,70,300,40)
        UserGUI.lblHR2.setFont(font)
        UserGUI.lblHR2.setText("Heart Rate: 0 BPM")
        
        UserGUI.Plot_Signal = pg.PlotWidget(UserGUI)
        
        UserGUI.Plot_Signal.move(660,220)
        UserGUI.Plot_Signal.resize(480,192)
        UserGUI.Plot_Signal.setLabel('bottom', "Signal") 
        
        UserGUI.Plot_FFT = pg.PlotWidget(UserGUI)
        
        UserGUI.Plot_FFT.move(660,425)
        UserGUI.Plot_FFT.resize(480,192)
        UserGUI.Plot_FFT.setLabel('bottom', "FFT") 
        
        UserGUI.timer = pg.QtCore.QTimer()
        UserGUI.timer.timeout.connect(UserGUI.update)
        UserGUI.timer.start(200)
        
        
        UserGUI.statusBar = QStatusBar()
        UserGUI.statusBar.setFont(font)
        UserGUI.setStatusBar(UserGUI.statusBar)

        UserGUI.c = Communicate()
        UserGUI.c.closeApp.connect(UserGUI.close)

        UserGUI.setGeometry(100,100,1160,640)

        UserGUI.setWindowTitle("Heart Rate Monitor")
        UserGUI.show()
        
        
    def update(UserGUI):
        UserGUI.Plot_Signal.clear()
        UserGUI.Plot_Signal.plot(UserGUI.compute.samples[20:],pen='g')

        UserGUI.Plot_FFT.clear()
        UserGUI.Plot_FFT.plot(np.column_stack((UserGUI.compute.freqs, UserGUI.compute.fft)), pen = 'g')
        
    def center(UserGUI):
        qr = UserGUI.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        UserGUI.move(qr.topLeft())
        
    def closeEvent(UserGUI, event):
        reply = QMessageBox.question(UserGUI,"Message", "Are you sure want to quit",
            QMessageBox.Yes|QMessageBox.No, QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            event.accept()
            UserGUI.input.stop()
            cv2.destroyAllWindows()
        else: 
            event.ignore()
    
    def selectInput(UserGUI):
        UserGUI.reset()
        if UserGUI.cbbInput.currentIndex() == 0:
            UserGUI.input = UserGUI.webcam
            print("Input: Webcam")
            UserGUI.statusBar.showMessage("Input: Webcam",5000)
        elif UserGUI.cbbInput.currentIndex() == 1:
            UserGUI.input = UserGUI.video
            print("Input: Video")
            UserGUI.statusBar.showMessage("Input: Video",5000)
    
    def key_handler(UserGUI):
        UserGUI.pressed = waitKey(1) & 255 
        if UserGUI.pressed == 27: 
            print("[INFO] Exiting")
            UserGUI.webcam.stop()
            sys.exit()
    
    def openFileDialog(UserGUI):
        UserGUI.dirname = QFileDialog.getOpenFileName(UserGUI, 'OpenFile',r"C:\Users")
        UserGUI.statusBar.showMessage("File Name: " + UserGUI.dirname,5000)
    
    def reset(UserGUI):
        UserGUI.compute.reset()
        UserGUI.lblDisplay.clear()
        UserGUI.lblDisplay.setStyleSheet("background-color: #000000")

    @QtCore.pyqtSlot()
    def main_loop(UserGUI):
        frame = UserGUI.input.get_frame()

        UserGUI.compute.frame_in = frame
        UserGUI.compute.run()
        
        cv2.imshow("Processed", frame)
        
        UserGUI.frame = UserGUI.compute.frame_out 
        UserGUI.f_fr = UserGUI.compute.frame_ROI
		
        UserGUI.bpm = UserGUI.compute.bpm 
        
        UserGUI.frame = cv2.cvtColor(UserGUI.frame, cv2.COLOR_RGB2BGR)
        cv2.putText(UserGUI.frame, "FPS "+str(int(UserGUI.compute.fps)),
                       (20,460), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 255),2)
        img = QImage(UserGUI.frame, UserGUI.frame.shape[1], UserGUI.frame.shape[0], 
                        UserGUI.frame.strides[0], QImage.Format_RGB888)
        UserGUI.lblDisplay.setPixmap(QPixmap.fromImage(img))
        
        UserGUI.f_fr = cv2.cvtColor(UserGUI.f_fr, cv2.COLOR_RGB2BGR)
		
        UserGUI.f_fr = np.transpose(UserGUI.f_fr,(0,1,2)).copy()
        f_img = QImage(UserGUI.f_fr, UserGUI.f_fr.shape[1], UserGUI.f_fr.shape[0], 
                       UserGUI.f_fr.strides[0], QImage.Format_RGB888)
        UserGUI.lblROI.setPixmap(QPixmap.fromImage(f_img))
        
        UserGUI.lblHR.setText("Frequency: " + str(int(UserGUI.bpm)) + " Hz")
        if UserGUI.compute.bpms.__len__() >30:
            if(max(UserGUI.compute.bpms-np.mean(UserGUI.compute.bpms))<15):
                UserGUI.lblHR2.setText("Heart Rate: " + str(int(np.mean(UserGUI.compute.bpms))) + " BPM")

        UserGUI.key_handler() 

    def run(UserGUI, input):
        UserGUI.reset()
        input = UserGUI.input
        UserGUI.input.dirname = UserGUI.dirname
        if UserGUI.input.dirname == "" and UserGUI.input == UserGUI.video:
            print("choose a video first")
            UserGUI.statusBar.showMessage("choose a video first",5000)
            return
        if UserGUI.status == False:
            UserGUI.status = True
            input.start()
            UserGUI.btnStart.setText("Stop")
            UserGUI.cbbInput.setEnabled(False)
			
            UserGUI.lblHR2.clear()
            while UserGUI.status == True:
                UserGUI.main_loop()
        elif UserGUI.status == True:
            UserGUI.status = False
            input.stop()
            UserGUI.btnStart.setText("Start")
            UserGUI.cbbInput.setEnabled(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = HRM()
    while ex.status == True:
        ex.main_loop()

    sys.exit(app.exec_())