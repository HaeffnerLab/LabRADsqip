import time
from twisted.internet.defer import inlineCallbacks
from twisted.internet.threads import deferToThread
from PyQt4 import QtGui, QtCore

class IA3133Widget(QtGui.QFrame):
    def __init__(self,reactor, parent=None):
        super(IA3133Widget, self).__init__(parent)
        self.reactor = reactor
        self.connect()
        
    @inlineCallbacks
    def connect(self):
        from labrad.wrappers import connectAsync
        self.cxn = yield connectAsync()
        self.relayserver = self.cxn.sqip_expcontrol_ia_3133
        try:            
            self.dmmserver = self.cxn.keithley_2100_dmm
            self.dmmserver.select_device('sqip_expcontrol GPIB Bus - USB0::0x05E6::0x2100::1243106')
        except Exception as e:
            pass
        self.setupWidget()
        self.relayList = [8, 9, 10] #[2,3,5,6,7,8,9,14,15,16,17,18,19,20,21,22,23,24,25] #,3,5,7,6,4
        self.threshold = 9.0
                        
    def setupWidget(self): 
        layout = QtGui.QGridLayout()
        relayBox = QtGui.QGroupBox('Channels') 
        relayBox.setFont(QtGui.QFont('MS Shell Dlg 2',pointSize=16))
        relaygrid = QtGui.QGridLayout()  
        relayBox.setLayout(relaygrid) 
        measBox = QtGui.QGroupBox('Measure') 
        measBox.setFont(QtGui.QFont('MS Shell Dlg 2',pointSize=16))
        measgrid = QtGui.QGridLayout()  
        measBox.setLayout(measgrid)   
        
        self.setGeometry(300, 300, 250, 150)
        self.setFrameStyle(QtGui.QFrame.Panel  | QtGui.QFrame.Raised)
        self.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        
        self.title1 = QtGui.QLabel('Channel')
        self.title2 = QtGui.QLabel()
        self.lcd = QtGui.QLCDNumber()
        self.lcd.setLineWidth(2)
        self.lcd.setNumDigits(2)
        self.lcd.setFont(QtGui.QFont('MS Shell Dlg 2',pointSize=20))
        self.lcd.setSegmentStyle(self.lcd.Filled)
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Foreground,QtCore.Qt.blue)
        self.lcd.setPalette(palette)
        self.tex = QtGui.QDoubleSpinBox()
        self.tex.setFont(QtGui.QFont('MS Shell Dlg 2',pointSize=20))
        self.tex.setDecimals(3)
        self.tex.setRange(-1e9,1e9)
        self.tex.setSuffix(' Volts')
        self.tex.setReadOnly(True)
        self.startButn = QtGui.QPushButton('Start')
        self.startButn.setFont(QtGui.QFont('MS Shell Dlg 2',pointSize=14))
        self.startButn.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        self.stopButn = QtGui.QPushButton('Stop')
        self.stopButn.setFont(QtGui.QFont('MS Shell Dlg 2',pointSize=14))
        self.stopButn.setCheckable(True)
        self.stopButn.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        self.textWin = QtGui.QTextBrowser()
        #self.textWin.setReadOnly(True)
        self.textWin.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        
        self.startButn.clicked.connect(self.Start)
        measgrid.addWidget(self.lcd, 0, 0)
        measgrid.addWidget(self.tex, 0, 1)
        measgrid.addWidget(self.startButn, 1,1)
        measgrid.addWidget(self.stopButn, 2,1)
        measgrid.addWidget(self.textWin, 3,1)
        
        for num in range(0,25):
            radio = QtGui.QRadioButton(str(num + 1), self)
            if (num<13):
                relaygrid.addWidget(radio,num + 1,1)
                radio.clicked.connect(self.activate(num))
            else:
                relaygrid.addWidget(radio,num-12,2)
                radio.clicked.connect(self.activate(num))
                
        self.Off = QtGui.QPushButton('Turn Off All')
        relaygrid.addWidget(self.Off, 7 , 3)
        self.Off.clicked.connect(self.deactiV)
                
        layout.addWidget(relayBox, 0, 1)
        layout.addWidget(measBox, 0, 0)
        self.setLayout(layout)
    
    @inlineCallbacks
    def Start(self, state = None):
        print 'Measuring'  
        self.stopButn.setChecked(False)  
        state = False
        while(state == False):
            for order,num in enumerate(self.relayList): 
                num2 = num - 1
                self.relayserver.activate_relay(num2)
                val = 0
                try:
                    val = yield self.dmmserver.get_dc_volts()
                except:
                    pass
                #val = yield self.dmmserver.get_resistance()
                print num, val
                self.lcd.display(str(num))
                self.tex.setValue(val)
                if val < self.threshold:
                    self.textWin.setText('Crossed threshold in channel {0}'.format(num))
                    #print val
                if self.stopButn.isChecked():
                    state = True
                    break
                time.sleep(2)
        else:
            yield self.relayserver.deactivateall()
        
    def activate(self, num):
        @inlineCallbacks
        def func(state):
            yield self.relayserver.activate_relay(num)
        return func
        
    @inlineCallbacks
    def deactiV(self, evt = None):
        yield self.relayserver.deactivateall()
        
    def closeEvent(self, x):
        self.reactor.stop()
        
if __name__=="__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    IA3133Widget = IA3133Widget(reactor)
    IA3133Widget.setWindowTitle('Relay Control')
    IA3133Widget.show()
    reactor.run()