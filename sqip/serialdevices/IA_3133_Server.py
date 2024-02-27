"""
### BEGIN NODE INFO
[info]
name = IA3133 server
version = 1.0
description = 
instancename = %LABRADNODE% IA3133 server

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""

from serialdeviceserver_baud import SerialDeviceServer, setting, inlineCallbacks, SerialDeviceError, SerialConnectionError, PortRegError
from labrad.types import Error
from twisted.internet import reactor
from twisted.internet.defer import returnValue
from labrad.server import Signal
from labrad.units import WithUnit
import time

SIGNALID = 209068

class IA3133server(SerialDeviceServer):
    name = '%LABRADNODE% IA 3133'
    regKey = 'IA3133'
    port = '026'
    serNode = 'sqip_expcontrol'
    timeout = WithUnit(1.0, 's')
    baudrate = 19200
    xonxoff = True
    onNewUpdate = Signal(SIGNALID, 'signal: settings updated', '(sv)')
    defaultState = '32'
    
    @inlineCallbacks
    def initServer(self):
        if not self.regKey or not self.serNode: raise SerialDeviceError( 'Must define regKey and serNode attributes' )
        port = yield self.getPortFromReg( self.regKey )
        self.port = port
        try:
            serStr = yield self.findSerial(self.serNode)
            self.initSerial( serStr, port )
        except SerialConnectionError, e:
            self.ser = None
            if e.code == 0:
                print 'Could not find serial server for node: %s' % self.serNode
                print 'Please start correct serial server'
            elif e.code == 1:
                print 'Error opening serial connection'
                print 'Check set up and restart serial server'
            else: raise
        
        yield self.ser.write('!01E00000000\r') # initialize with all deactivated

    @setting(1, "Identify", returns='s')
    def identify(self, c):
        '''Ask instrument to identify itself'''
        command = self.IdenStr()
        self.ForceRead() #expect a reply from instrument
        answer = yield self.ser.readline()
        returnValue(answer)
        
    @setting(2, 'Activate relay', label = 'i', returns = '' )
    def activateRelay( self, c, label):
        """Activates relay N.
        """
        #print label
        cmd = self.actRelayStr(label)
        yield self.ser.write(cmd)
        
    @setting(3, 'De-activate relay', label = 'i', returns = '' )
    def deactivateRelay( self, c, label):
        """De-activates relay N.
        """
        #print label
        cmd = self.deactRelayStr(label)
        yield self.ser.write(cmd)
        
    @setting(4, 'DeactivateAll', returns = '')
    def deactivateAll(self, c):
        yield self.ser.write('!01E00000000\r')
        
    @setting(5, 'Close', returns = '')
    def close(self, c):
        self.ser.close()


    @inlineCallbacks
    def ForceRead(self):
        command = self.ForceReadStr()
        yield self.ser.write(command)
  
    def IdenStr(self):
        return '?010\r'

    # string to force read
    def ForceReadStr(self):
        return '++read eoi' + '\n'
    
    def ChangeHex(self, label):
        if (label<16):
            x = '0'+hex(label).split('x')[1]
        else:
            x = hex(label).split('x')[1]
        return x
    
    def actRelayStr(self, label):
        return '!013'+ self.ChangeHex(label) + '\r'
    
    def deactRelayStr(self, label):
        return '!014'+ self.ChangeHex(label) + '\r'

if __name__ == "__main__":
    from labrad import util
    util.runServer( IA3133server() )
