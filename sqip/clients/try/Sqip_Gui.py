
from PyQt4 import QtGui
a = QtGui.QApplication( [])

#import server libraries



from labrad.server import LabradServer, setting, Signal, inlineCallbacks
import SqipGUI

"""
### BEGIN NODE INFO
[info]
name =  Sqip_GUI
version = 1.0
description = 
instancename = Sqip_GUI
cmdline = %PYTHON% %FILE%
timeout = 20
[shutdown]
message = 987654321
timeout = 5
### END NODE INFO
"""

class Sqip_GUI(LabradServer):
    
    """ Methods for controlling graphing """

    name = "Sqip_GUI"

    @inlineCallbacks
    def initServer(self):
        self.listeners = set()
        a = QtGui.QApplication( [] )
        import common.clients.qt4reactor as qt4reactor
        # qt4reactor.install()
        from twisted.internet import reactor
        sqipGUI = SQIP_GUI(reactor)
        sqipGUI.setWindowTitle('Sqip GUI')
        sqipGUI.show()
        reactor.run()

if __name__ == '__main__':
    from labrad import util
    print('try')
    util.runServer(Sqip_GUI())



