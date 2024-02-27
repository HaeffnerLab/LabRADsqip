from scan_cavity import scan_cavity
import labrad
from numpy import import linspace

class scan_cavity_854(scan_cavity):
    
    name = 'Scan Cavity 854'
    required_parameters = [
                           ('CavityScans','average'),
                           ('CavityScans','cavity_scan_854'),
                           ('CavityScans','point_delay'),
                           ('CavityScans', 'moving_resolution'),
                           ]
    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.cavity_name = '854'
        cxnlab = labrad.connect('192.168.169.49')
        self.1d = cxnlab.laserdac
        self.pmt = cxn.normalpmtflow
        self.dv = cxn.data_vault
        self.average = int(self.parameters.CavityScans.average)
        self.resolution = self.parameters.CavityScans.moving_resolution
        self.point_delay = self.parameters.CavityScans.point_delay['s']
        minim,maxim,steps = self.parameters.CavityScans.cavity_scan_854
        self.minim = minim = minim['mV']; self.maxim = maxim = maxim['mV']
        self.scan = linspace(minim,maxim,steps)
        self.init_voltage = self.1d.getvoltage(self.cavity_name)
        self.navigate_data_vault()
        
if __name__ == '__main__':
    #normal way to launch
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = scan_cavity_854(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident) 