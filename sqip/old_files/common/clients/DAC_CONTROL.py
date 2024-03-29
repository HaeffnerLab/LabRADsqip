from PyQt4 import QtGui, QtCore, uic
from qtui.QCustomSpinBox import QCustomSpinBox
from twisted.internet.defer import inlineCallbacks, returnValue
from common.okfpgaservers.dacserver.DacConfiguration import hardwareConfiguration as hc


UpdateTime = 100 # ms
SIGNALID = 270836
SIGNALID2 = 270835

class MULTIPOLE_CONTROL(QtGui.QWidget):
    def __init__(self, reactor, parent=None):
        super(MULTIPOLE_CONTROL, self).__init__(parent)
        self.reactor = reactor
        self.makeGUI()
        self.connect()        
   
    def makeGUI(self):
        self.controls = {k: QCustomSpinBox(k, (-2.,2.)) for k in hc.multipoles}
        self.controls['U1'] = QCustomSpinBox('U1', (-2., 2.))
        self.controls['U2'] = QCustomSpinBox('U2', (0., 20.))
        self.controls['U3'] = QCustomSpinBox('U3', (-2., 2.))
        #self.controls['U4'] = QCustomSpinBox('U4', (-4., 4.))
        self.multipoleValues = {k: 0.0 for k in hc.multipoles}
        self.ctrlLayout = QtGui.QVBoxLayout()
        for k in hc.multipoles:
            self.ctrlLayout.addWidget(self.controls[k])        
        self.multipoleFileSelectButton = QtGui.QPushButton('Set C File')
        self.ctrlLayout.addWidget(self.multipoleFileSelectButton)

        self.inputUpdated = False
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.sendToServer)
        self.timer.start(UpdateTime)   

        for k in hc.multipoles:
            self.controls[k].onNewValues.connect(self.inputHasUpdated)
        self.multipoleFileSelectButton.released.connect(self.selectCFile)
        self.setLayout(self.ctrlLayout)

    @inlineCallbacks
    def connect(self):
        from labrad.wrappers import connectAsync
        from labrad.types import Error
        self.cxn = yield connectAsync()
        self.dacserver = yield self.cxn.dac_server
        yield self.setupListeners()
        yield self.followSignal(0, 0)
        
    def inputHasUpdated(self):
        self.inputUpdated = True
        for k in hc.multipoles:
            self.multipoleValues[k] = round(self.controls[k].spinLevel.value(), 3)
        
    def sendToServer(self):
        if self.inputUpdated:
            self.dacserver.set_multipole_values(self.multipoleValues.items())
            self.inputUpdated = False
    
    @inlineCallbacks        
    def selectCFile(self):
        fn = QtGui.QFileDialog().getOpenFileName()
        yield self.dacserver.set_multipole_control_file(str(fn))        
        self.inputHasUpdated()
        
    @inlineCallbacks    
    def setupListeners(self):
        yield self.dacserver.signal__ports_updated(SIGNALID)
        yield self.dacserver.addListener(listener = self.followSignal, source = None, ID = SIGNALID) 
        
    @inlineCallbacks
    def followSignal(self, x, s):
        try:
            multipoles = yield self.dacserver.get_multipole_values()
            for (k,v) in multipoles:
                self.controls[k].setValueNoSignal(v)
        except: print '...'  

    def closeEvent(self, x):
        self.reactor.stop()  

class CHANNEL_CONTROL (QtGui.QWidget):
    def __init__(self, reactor, parent=None):
        super(CHANNEL_CONTROL, self).__init__(parent)
        self.reactor = reactor
        self.makeGUI()
        self.connect()
     
    def makeGUI(self):
        self.dacDict = dict(hc.elecDict.items() + hc.smaDict.items())
        self.controls = {k: QCustomSpinBox(k, self.dacDict[k].allowedVoltageRange) for k in self.dacDict.keys()}
        layout = QtGui.QGridLayout()
        smaBox = QtGui.QGroupBox('SMA Out')
        smaLayout = QtGui.QVBoxLayout()
        smaBox.setLayout(smaLayout)
        elecBox = QtGui.QGroupBox('Electrodes')
        elecLayout = QtGui.QGridLayout()
        elecBox.setLayout(elecLayout)
        layout.addWidget(smaBox, 0, 0)
        layout.addWidget(elecBox, 0, 1)

        for k in hc.smaDict:
            smaLayout.addWidget(self.controls[k], alignment = QtCore.Qt.AlignRight)
        for k in hc.elecDict:
            if (int(k) == hc.centerElectrode):
                labl = str(k) + '(CNT)'
                self.controls[k].title.setText(labl)
                elecLayout.addWidget(self.controls[k], hc.numElectrodes/2, 1)
            elif int(k) <= hc.numElectrodes/2:
                elecLayout.addWidget(self.controls[k], hc.numElectrodes/2 - int(k), 0)
            elif int(k) > hc.numElectrodes/2:
                elecLayout.addWidget(self.controls[k], hc.numElectrodes - 0 - int(k), 2)  
            elif (int(k) == hc.numElectrodes):
                elecLayout.addWidget(self.controls[k], hc.numElectrodes + 1 - int(k), 2)      
        spacer = QtGui.QSpacerItem(20,40,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.MinimumExpanding)
        smaLayout.addItem(spacer)

        self.inputUpdated = False                
        self.timer = QtCore.QTimer(self)        
        self.timer.timeout.connect(self.sendToServer)
        self.timer.start(UpdateTime)
        
        for k in self.dacDict.keys():
            self.controls[k].onNewValues.connect(self.inputHasUpdated(k))

        layout.setColumnStretch(1, 1)                   
        self.setLayout(layout)	
            
    @inlineCallbacks
    def connect(self):
        from labrad.wrappers import connectAsync
        from labrad.types import Error
        self.cxn = yield connectAsync()
        self.dacserver = yield self.cxn.dac_server
        yield self.setupListeners()
        yield self.followSignal(0, 0)

    def inputHasUpdated(self, name):
        def iu():
            self.inputUpdated = True
            self.changedChannel = name
        return iu

    def sendToServer(self):
        if self.inputUpdated:            
            self.dacserver.set_individual_analog_voltages([(self.changedChannel, round(self.controls[self.changedChannel].spinLevel.value(), 3))])
            self.inputUpdated = False
            
    @inlineCallbacks    
    def setupListeners(self):
        yield self.dacserver.signal__ports_updated(SIGNALID2)
        yield self.dacserver.addListener(listener = self.followSignal, source = None, ID = SIGNALID2)
    
    @inlineCallbacks
    def followSignal(self, x, s):
        av = yield self.dacserver.get_analog_voltages()
        for (c, v) in av:
            self.controls[c].setValueNoSignal(v)

    def closeEvent(self, x):
        self.reactor.stop()        

class CHANNEL_MONITOR(QtGui.QWidget):
    def __init__(self, reactor, parent=None):
        super(CHANNEL_MONITOR, self).__init__(parent)
        self.reactor = reactor        
        self.makeGUI()
        self.connect()
        
    def makeGUI(self):      
        self.dacDict = dict(hc.elecDict.items() + hc.smaDict.items())
        self.displays = {k: QtGui.QLCDNumber() for k in self.dacDict.keys()}               
        layout = QtGui.QGridLayout()
        smaBox = QtGui.QGroupBox('SMA Out')
        smaLayout = QtGui.QGridLayout()
        smaBox.setLayout(smaLayout)
        elecBox = QtGui.QGroupBox('Electrodes')
        elecLayout = QtGui.QGridLayout()
        elecLayout.setColumnStretch(1, 2)
        elecLayout.setColumnStretch(3, 2)
        elecLayout.setColumnStretch(5, 2)
        elecBox.setLayout(elecLayout)
        layout.addWidget(smaBox, 0, 0)
        layout.addWidget(elecBox, 0, 1)

        for k in hc.smaDict:
            self.displays[k].setAutoFillBackground(True)
            smaLayout.addWidget(QtGui.QLabel(k), self.dacDict[k].smaOutNumber, 0)
            smaLayout.addWidget(self.displays[k], self.dacDict[k].smaOutNumber, 1)
            s = hc.smaDict[k].smaOutNumber+1
        for k in hc.elecDict:
            self.displays[k].setAutoFillBackground(True)
            if (int(k) == hc.centerElectrode):
                labl = str(k) + '(CNT)'
                elecLayout.addWidget(QtGui.QLabel(labl), hc.numElectrodes/2 + 1, 2)
                elecLayout.addWidget(self.displays[k], hc.numElectrodes/2 + 1, 3)
            elif int(k) <= hc.numElectrodes/2:
                elecLayout.addWidget(QtGui.QLabel(k), hc.numElectrodes/2 + 1 - int(k), 0)
                elecLayout.addWidget(self.displays[k], hc.numElectrodes/2 + 1 - int(k), 1)
            elif int(k) > hc.numElectrodes/2:
                elecLayout.addWidget(QtGui.QLabel(k), hc.numElectrodes - int(k), 4)
                elecLayout.addWidget(self.displays[k], hc.numElectrodes - int(k), 5) 

        spacer = QtGui.QSpacerItem(20,40,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.MinimumExpanding)
        smaLayout.addItem(spacer, s, 0,10, 2)  

        self.setLayout(layout)  
                
    @inlineCallbacks
    def connect(self):
        from labrad.wrappers import connectAsync
        from labrad.types import Error
        self.cxn = yield connectAsync()
        self.dacserver = yield self.cxn.dac_server
        self.ionInfo = {}
        yield self.setupListeners()
        yield self.followSignal(0, 0)       
        
    @inlineCallbacks    
    def setupListeners(self):
        yield self.dacserver.signal__ports_updated(SIGNALID2)
        yield self.dacserver.addListener(listener = self.followSignal, source = None, ID = SIGNALID2)
    
    @inlineCallbacks
    def followSignal(self, x, s):
        av = yield self.dacserver.get_analog_voltages()
        brightness = 210
        darkness = 255 - brightness           
        for (k, v) in av:
            self.displays[k].display(float(v)) 
            if abs(v) > 30:
                self.displays[k].setStyleSheet("QWidget {background-color: orange }")
            else:
                R = int(brightness + v*darkness/30.)
                G = int(brightness - abs(v*darkness/30.))
                B = int(brightness - v*darkness/30.)
                hexclr = '#%02x%02x%02x' % (R, G, B)
                self.displays[k].setStyleSheet("QWidget {background-color: "+hexclr+" }")

    def closeEvent(self, x):
        self.reactor.stop()

class DAC_Control(QtGui.QMainWindow):
    def __init__(self, reactor, parent=None):
        super(DAC_Control, self).__init__(parent)
        self.reactor = reactor

        channelControlTab = self.buildChannelControlTab()        
        multipoleControlTab = self.buildMultipoleControlTab()
        # scanTab = self.buildScanTab()
        tab = QtGui.QTabWidget()
        tab.addTab(multipoleControlTab,'&Multipoles')
        tab.addTab(channelControlTab, '&Channels')
        # tab.addTab(scanTab, '&Scans')
        self.setWindowTitle('DAC Control')
        self.setCentralWidget(tab)
    
    def buildMultipoleControlTab(self):
        widget = QtGui.QWidget()
        gridLayout = QtGui.QGridLayout()
        gridLayout.addWidget(CHANNEL_MONITOR(self.reactor),0,0)
        gridLayout.addWidget(MULTIPOLE_CONTROL(self.reactor),0,1)
        widget.setLayout(gridLayout)
        return widget

    def buildChannelControlTab(self):
        widget = QtGui.QWidget()
        gridLayout = QtGui.QGridLayout()
        gridLayout.addWidget(CHANNEL_CONTROL(self.reactor),0,0)
        widget.setLayout(gridLayout)
        return widget
        
    def buildScanTab(self):
        from SCAN_CONTROL import Scan_Control_Tickle
        widget = QtGui.QWidget()
        gridLayout = QtGui.QGridLayout()
        gridLayout.addWidget(Scan_Control_Tickle(self.reactor, 'Ex1'), 0, 0)
        gridLayout.addWidget(Scan_Control_Tickle(self.reactor, 'Ey1'), 0, 1)
        widget.setLayout(gridLayout)
        return widget
    
    def closeEvent(self, x):
        self.reactor.stop()  

if __name__ == "__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    DAC_Control = DAC_Control(reactor)
    DAC_Control.show()
    reactor.run()
