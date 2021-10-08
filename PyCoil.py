# -*- coding: utf-8 -*-
"""
PyCoil main file
"""

from PyQt4 import QtGui, QtCore  # Import the PyQt4 module we'll need
import sys  # We need sys so that we can pass argv to QApplication
from time import strftime
import time
import os
import csv

import Files.CoilGUI  # This file holds our MainWindow and all design related things
#get it with QtDesigner - Save as .ui and then run
# 'pyuic4 design.ui -o design.py' in an console
# it also keeps events etc that we defined in Qt Designer
from Files.Caio_ctype import Caio #Import the low_level commands to the AnalogOutput Device
import Files.Function as signal #Import sinewave, constant, writebuffer, direction
import numpy as np

#get start timestamp
#startprog = datetime.datetime.now() 

#initialize device
device = Caio()
# device.DaveiceName = 'AO-1604LX-USB'
# device.DeviceName == 'AIO001'

#get current dir and create \Log folder
curDir = os.getcwd()
if not os.path.exists(curDir+'\Logs'):
    os.mkdir('Logs')
os.chdir(curDir+'\Logs')

#create Logfile
name_logfile = strftime("PyCoil_%Y%m%d__%H_%M_%S.txt")
text_file = open(name_logfile, 'w')


#Start the GUI
class PyCoilApp(QtGui.QMainWindow, Files.CoilGUI.Ui_MainWindow):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)  # This is defined in CoilGUI.py file automatically
        
        
        self.btn_start.clicked.connect(self.startCoil)  # Connect btn_start with the sartCoil function
        self.btn_stop.clicked.connect(self.stopCoil)
        self.btn_close.clicked.connect(self.closeEvent)
        self.menu_close.triggered.connect(self.closeEvent)
        self.menu_calib.triggered.connect(self.getCalibration)
        self.manue_newcalib.triggered.connect(self.newCalibration)
        self.actionShow_drawing.triggered.connect(self.sphDef)
   
        self.initUI()
        
######### Never change anything outside this area          
    def initUI(self):
        self.label_status.setText('Status for Session: ' + name_logfile)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.Time)
        self.timer.start(1000)
        self.lcd_time.display(strftime("%H:%M:%S"))
        self.fixedDir.show()
        self.fixedDir.isActiveWindow()
        self.tabWidget.setCurrentIndex(0)
        self.PhiBox.setValue(0)
        self.ThetaBox.setValue(90)
        self.box_bfield.setValue(1)
        self.box_freq.setValue(1)
        self.calc_scripttime.setText(str(self.npoints_Dwell.value()*(self.movetime.value()+self.dwelltime.value())))




        # check if device is connected
        if device.Id == -1:  # Id=0 if properly connected
            QtGui.QMessageBox.information(self, 'Error: No Device found', 'No device (AO-1604LX-USB) found. Connect device properly and restart PyCoil')
            #self.deleteLater()
            text_file.close()
            os.remove(name_logfile)
            return
        print '_FOUND ' + device.DeviceName
        print '_KNOWN AS ' + device.Device
        print ' status ' + str(device.status) +'\n DeviceType '+ str(device.DeviceType) +'\n Id '+ str(device.Id) +'\n repeat_times '+ str(device.repeat_times)

        string = '### New session' + '\n' + strftime("### %Y-%m-%d %H:%M:%S")
        self.text_status.append(string)
        text_file.write(string)
        self.getCalibration()

        
    def getCalibration(self):
        #global curCalib
        curCalib=[]
        #os.listdir(curDir+'\calibration')
        if not os.path.exists(curDir+'\calibration') or signal.list_f_ext(curDir+'\calibration', 'txt') == []:
            QtGui.QMessageBox.information(self,'Error: No calibration file',
            'No calibration file found in '+ curDir + '\calibration' + '\n' +
            'Using Standard calibration instead')
            curCalib = [0.01,0.01,0.01]
            filename = 'Standard calibration'
            
        else:
            #get available calibration files
            items = signal.list_f_ext(curDir+'\calibration', 'txt')
            #choose a file
            filename, ok = QtGui.QInputDialog.getItem(self, 'Choose calibration', 'Choose one of the calibration files found in \n'
            + curDir + '\calibration',
            items, 0, False)
            #open file and extract values
            if ok:
                #print(curDir + "\calibration\\" + filename)
                try:
                    with open(curDir + "\calibration\\" + filename, mode='r') as f:
                        reader = csv.reader(f)
                        row1 = next(reader)
                        curCalib = [float(row1[0]), float(row1[1]), float(row1[2])]
                        print('current calibration:'+ str(curCalib))

                except:
                    QtGui.QMessageBox.information(self,'Wrong input','Cannot read calibration file syntax\n'+
                                                  'Using standard calibration .01,.01,.01 instead!')
                    curCalib = [0.01, 0.01, 0.01]
                    filename = 'Standard calibration'
    
#                string= ('Set calibration to: '+str(curCalib)+' (from '+filename+')')
#                self.text_status.append(string)
#                text_file.write('\n' + string)
            
            else:
                QtGui.QMessageBox.information(self,'Aborted','Loading calibration aborted!\n'+
                    'Using standard calibration .01,.01,.01 instead!')
                curCalib = [0.01,0.01,0.01]
                filename = 'Standard calibration'
                
        string= ('Set calibration to: '+str(curCalib)+' (from ' +filename+')')
        self.curCalib=curCalib
        self.text_status.append(string)
        text_file.write('\n' + string)


      
        
    def newCalibration(self):
        
        x, xok = QtGui.QInputDialog.getDouble(self, 'Calibration factor for X',
                'Calibration factor is the slope of B_real/B_teoretical \n \n Enter calibration value for X', value=self.curCalib[0], decimals = 5)
        y, yok = QtGui.QInputDialog.getDouble(self, 'Calibration factor for Y',
                'Calibration factor is the slope of B_real/B_teoretical \n \n Enter calibration value for Y', value=self.curCalib[1],decimals = 5)
        z, zok = QtGui.QInputDialog.getDouble(self, 'Calibration factor for Z',
                'Calibration factor is the slope of B_real/B_teoretical \n \n Enter calibration value for Z', value=self.curCalib[2],decimals = 5)
        if xok and yok and zok:
            curCalib = [x,y,z]
            
            if not os.path.exists(curDir+'\calibration'):
                os.mkdir('calibration')
            
            os.chdir(curDir+'\calibration')        
            cf = open('Calib'+name_logfile,'w')
            cal = str(x)+','+str(y)+','+str(z)
            cf.write(cal)
            cf.close()
            
            QtGui.QMessageBox.information(self,'Calibration successful','New calibration set: '+str(curCalib)+'\n'+
            'Saved calibration data as ...\calibration\\'+cf.name)
            
            string= ('Set calibration to: '+str(curCalib)+' (from '+'Calib'+name_logfile+')')
            self.text_status.append(string)
            text_file.write('\n' + string)

            print('current calibration:' + str(curCalib))
            self.curCalib=curCalib
        
        else:
            QtGui.QMessageBox.information(self,'Aborted','New calibration aborted! \n'+
            'Please try again')
    
    def Time(self):
        self.lcd_time.display(strftime("%H:%M:%S"))
        self.calc_scripttime.setText(str(self.npoints_Dwell.value()*(self.movetime.value()+self.dwelltime.value())))
            
            
    def startCoil(self):
        #time.sleep(0.5)
        device.tozero()
        #get B-field and freqeuncy
        b_field = self.box_bfield.value()
        freq = self.box_freq.value()

        #Set maximum values for B and f
        if b_field>80:  #General maximum for B
            device.tozero()
            self.label_field.setText('!-ERROR-!\n Too high field! \n max. B < 80G ! ')
            return

        #check which signal is selected
            # first sc check if free direction is selcted
        if self.tabWidget.currentIndex() == 0:
            print 'fixed direction'
        if self.tabWidget.currentIndex() == 1:
            print 'free direction'
            #curCalib=[1, 1, 1]
            theta = np.deg2rad(self.ThetaBox.value())
            phi = np.deg2rad(self.PhiBox.value())
            # spherical coordinates in x,y,z
            spXarray = np.sin(theta) * np.cos(phi)*np.ones((5, 1))
            spYarray = np.sin(theta) * np.sin(phi)*np.ones((5, 1))
            spZarray = np.cos(theta) * np.ones((5, 1))
            spX = spXarray * self.curCalib[0] * b_field
            spY = spYarray * self.curCalib[1] * b_field
            spZ = spZarray * self.curCalib[2] * b_field

            buf = signal.writebuffer(spX.round(15), spY.round(15), spZ.round(15))
            device.n_channels = 3  # set number of channels to 3
            device.buffer = buf
            device.start()
            string = (strftime("%H:%M:%S -- ") +  # add timestamp
                      'constant B-field along (Theta, Phi) = (' + str(np.rad2deg(theta).round(2)) + ', ' + str(np.rad2deg(phi).round(2)) +
                      ') // (x,y,z) = (' + str(spXarray[0].round(5)) + ', ' +str(spYarray[0].round(5)) + ', ' + str(spZarray[0].round(5)) +
                      ') , Amplitude: ' + str(b_field) +
                      'G // Frequency: ' + str(freq) + 'Hz')

            self.label_field.setText('constant field along \n(Theta, Phi) = (' + str(np.rad2deg(theta).round(2)) + ', ' + str(np.rad2deg(phi).round(2)) +
                                        ') \n(x,y,z) = (' +  str(spXarray[0].round(5)) + ', ' +str(spYarray[1].round(5)) + ', ' + str(spZarray[2].round(5)) + ')')

            # write status and new line to logfile
            self.text_status.append(string)
            text_file.write('\n' + string)
            return

        # run script with random motion
        if self.tabWidget.currentIndex() == 2:
            #print device.fs
            print 'run random motion Script'


            sample_points = self.npoints.value() # number of points on sphere

            script_duration = sample_points/freq
            step_duration = 1/freq
            device.fs=10*freq # real sampling is 10 times target sampling rate

            pt_vec = signal.golden_spiral(int(sample_points)) #create a 'random' trajectory on sphere with evenly space step size
            # Open Function.py to the trajectory

            # ____ OLD CODE ____
            # points = signal.traj_on_sphere(10)#create points on sphere with evenly distributed theta
            # random_vec = signal.spherical_points(int(sample_points)) #create randomly distributed points on a sphere
            # __________________
            # np.savetxt("C:/Temp/raw_N200.csv", pt_vec, delimiter=",")

            buf_array = np.repeat(pt_vec, device.fs*step_duration, axis=0) #create buffer array with the correct number of samples
            buf_array = buf_array*self.curCalib*b_field #and correct output voltage

            TTL = np.zeros((buf_array.shape[0], 1)) #create TTL trigger column
            TTL[0:int(device.fs*step_duration)] = 5 #set first value to 5 volts
            randTTL = np.append(buf_array, TTL, axis=1) #append column with zeros for TTL trigger


            buf_array = randTTL.round(15) #rename as buf_array again
            #np.savetxt("C:\Users\sachs\Documents\Random_rawN" + str(sample_points) + ".txt", buf_array, delimiter=",")
            device.n_channels = 4 #set 4 output channels
            device.buffer = buf_array
            device.start()

            string = (strftime("%H:%M:%S -- ") +  # add timestamp
                      'Artificial random motion script with Amplitude: ' + str(b_field) +
                      'G // Frequency: ' + str(freq) + 'Hz // Dwell: ' + str(step_duration) +'s and the following points [x, y, z]:'

                      )

            self.label_field.setText('Running random motion script with\n' + str(freq) + 'Hz (Dwell= '+ str(step_duration)+ 's) and ' + str(b_field) +
                                        'G\n\nPattern is repeated after '+  str(script_duration) + ' seconds!')


            self.text_status.append(string + ' .... (see .txt file for details)')
            text_file.write('\n' + string + '\n' + np.array2string(buf_array, precision=5, separator=',', edgeitems=5000, suppress_small=True))
            #device.fs=initial_sampling

            return


        # run script with fixed dwell time
        if self.tabWidget.currentIndex() == 3:
            #print device.fs
            print 'run fixed dwell time Script'


            sample_points = self.npoints_Dwell.value() # number of points on sphere
            step_duration = self.movetime.value() + self.dwelltime.value()

            script_duration = sample_points * step_duration
            device.fs=25*(1/float(step_duration)) # real sampling is 25 times target sampling rate

            if self.radBut_Dwell_XY.isChecked():
                modestring = '(circle)'
                pt_vec = signal.circleXY(int(sample_points)) #create circular trajectory in XY
            else:
                modestring = '(sphere)'
                pt_vec = signal.golden_spiral(int(sample_points)) #create a 'random' trajectory on sphere with evenly space step size

            buf_array = np.repeat(pt_vec, device.fs*step_duration, axis=0) #create buffer array with the correct number of samples
            buf_array = buf_array*self.curCalib*b_field #and correct output voltage

            #create TTL pulse in 4th column
            stepsondev = (int(device.fs * step_duration)) #number of points being sampled on device
            TTL_perStep = np.zeros((stepsondev, 1)) #create TTL trigger column for one step
            startidx = int(np.ceil(self.movetime.value() * device.fs)) #wait for movetime specified
            endidx = startidx+stepsondev/2 #trigger pulse length is half of device sampling freq.
            TTL_perStep[startidx:endidx] = 5 #set TTL high (5 volts)
            TTL = np.tile(TTL_perStep.T, sample_points).T #create array with correct number of samples

            randTTL = np.append(buf_array, TTL, axis=1) #append column with zeros for TTL trigger

            buf_array = randTTL.round(15) #rename as buf_array again

            device.n_channels = 4 #set 4 output channels
            device.buffer = buf_array
            device.start()

            string = (strftime("%H:%M:%S -- ") +  # add timestamp
                      'Dwell time script ' + modestring + ' with ' + str(sample_points) +' points,  Amplitude: ' + str(b_field) +
                      'G // Frequency: ' + str('%.2f' %(1/step_duration)) + 'Hz // Dwell time: ' + str(self.dwelltime.value()) +'s and the following coordinates [x, y, z]:'

                      )

            self.label_field.setText('Running Dwell time script' + modestring + 'with\n' + str('%.2f' %(1/step_duration)) + 'Hz (Dwell= '+ str(self.dwelltime.value())+ 's) and ' + str(b_field) +
                                        'G\n\nPattern is repeated after '+  str(script_duration) + ' seconds!')


            self.text_status.append(string + ' .... (see .txt file for details)')
            text_file.write('\n' + string + '\n' + np.array2string(buf_array, precision=5, separator=',', edgeitems=5000, suppress_small=True))
            #device.fs=initial_sampling

            return


    # otherwise use the fixed directions
        if self.const_field.isChecked():
            coil_signal = 'constant' 
            text = ('Constant along ')
        else:
            coil_signal = 'rotate'
            text = ('Rotation in ')
            if not (0 < freq <= 40):  # frequency range 0 to 40
                device.tozero()
                self.label_field.setText('!-ERROR-!\n No frequency set or\n Frequency too high \n max f < 40Hz ! ')
                return

        
        #direction negative?
        if self.neg_dir.isChecked():
           coil_dir = '-'       
        else:
            coil_dir = ''


            
        #check which direction is selected and append
        if self.x_dir.isChecked():
            coil_dir = coil_dir + 'x'
            self.label_field.setText(text + (coil_dir.upper() if self.const_field.isChecked() else 'Y-Z plane (along ' +coil_dir+')'))
        if self.y_dir.\
                isChecked():
            coil_dir = coil_dir + 'y'
            self.label_field.setText(text + (coil_dir.upper() if self.const_field.isChecked() else 'X-Z plane (along ' +coil_dir+')'))
        if self.z_dir.isChecked() == True:
            coil_dir = coil_dir + 'z'
            self.label_field.setText(text + (coil_dir.upper() if self.const_field.isChecked() else 'X-Y plane (along ' +coil_dir+')'))
        
        #set signal to zero ???
        #device.tozero()
        
        #write buffer and start output
        device.fs=1000
        buf = signal.direction(coil_dir, coil_signal, b_field, freq, samp=1000, calibration=self.curCalib) #try different samples
        device.n_channels = 3  # set number of channels to 3

        device.buffer = buf
        device.start()
        
        #status string
        string = (strftime("%H:%M:%S -- ") + #add timestamp
                                self.label_field.text() +
                                ', Amplitude: ' + str(b_field) +
                                'G // Frequency: ' + str(freq) + 'Hz')

        
        #write status and new line to logfile  
        self.text_status.append(string)
        text_file.write('\n' + string)

        #time.sleep(1)
        #add matplotlib/picture of signals in x,y,z
        
    def stopCoil(self):
        
        string= (strftime("%H:%M:%S -- ") +'Field stopped')
        self.text_status.append(string)
        text_file.write('\n' + string)

        self.label_field.setText('---- Field stopped ----')
        device.tozero()

    def sphDef(self):
        QtGui.QMessageBox.information(self, "Definition used", "The used coordinates are choosen according to the ISO definition:\n\n"
            "  Theta -- inclination or polar angle between z-axis and xy-plane,\n  Phi -- azimuthal angle in xy-plane, measured from x-axis\n\n"
                "  E.g. Theta=90, Phi=45 will lead to a vector in the xy-plane with coordiantes [0.7071, 0.7071, 0]")
        
    def closeEvent(self, event):
        device.tozero()
        #time.sleep(0.5)
        device.stop()
        device.reset_memory()
        device.reset_status()
        device.reset_device()
        #time.sleep(0.1  )

        path = os.getcwd()
        
        text_file.close()

        QtGui.QMessageBox.information(self, 'Saving Logfile...', 'Logfile saved as ' +
                                        name_logfile + ' in' + '\n' + path
                                        )
        self.deleteLater()


######### End of modification area

def main():
    app = QtGui.QApplication(sys.argv)  # A new instance of QApplication
    form = PyCoilApp()  # We set the form to be our PyCoilApp (design)
    form.show()  # Show the form
    sys.exit(app.exec_())  # and execute the app


if __name__ == '__main__':  # if we're running file directly and not importing it
    main()  # run the main function
