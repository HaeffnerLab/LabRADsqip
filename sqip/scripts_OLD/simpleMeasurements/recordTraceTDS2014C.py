import labrad
import numpy as np
import time
import scipy
import scipy.fftpack
from scipy import pi
from matplotlib import pyplot as plt

class Tektronix_Measure():
    '''
        Collect traces with Tektronix TDS 2014C
    '''
    
    def initialize(self):
        #servers
        self.cxn = cxn = labrad.connect()
        self.dv = dv = cxn.data_vault
        self.tek = tek = cxn.tektronixtds_server()
        tek.select_device('sqip_expcontrol GPIB Bus - USB0::0x0699::0x03A4::C014755')
        tek.setchannel(1)        
        
    def setup_data_vault(self):
        self.today = str(time.strftime("%Y%b%d",time.localtime()))
        print self.today
        self.dv.cd(['','QuickMeasurements','Scope Measurements', self.today], True)
        dependVariables = [('Volts', '1', 'V')]
        self.dv.new('Voltage Measurement',[('Time', 'sec')], dependVariables )
        self.dv.add_parameter('Window',['Voltage Measurement'])
        self.dv.add_parameter('plotLive','True')

    def record_trace(self):
        self.initialize()
        self.setup_data_vault()
        print 'Measuring...'
        #measurement 
        A = self.tek.getcurve()
        self.dat = np.asarray(A)
        self.dv.add(self.dat)
        print 'DONE'

    def analyze(self):
        '''
        self.dv.cd(['','QuickMeasurements','Scope Measurements', self.today], True)
        self.dv.open(number)
        '''
        [times, voltages] = self.dat.transpose()
        FFT = abs(scipy.fft(voltages))
        freqs = scipy.fftpack.fftfreq(voltages.size, times[1]-times[0])
        spec_intens = 20*scipy.log10(FFT)
        print spec_intens.max(), freqs[np.argmax(spec_intens)]
        
        plt.figure()
        plt.subplot(211)
        plt.plot(times,voltages,'-.')
        plt.title('Voltage Trace')
        plt.xlabel('time ()')
        plt.ylabel('Voltage ()')
        plt.grid(True,'both')
        plt.subplot(212)
        plt.plot(freqs,spec_intens)
        plt.title('FFT')
        plt.show()

if __name__ == '__main__':
    exprt = Tektronix_Measure()
    exprt.record_trace()
    exprt.analyze()
    