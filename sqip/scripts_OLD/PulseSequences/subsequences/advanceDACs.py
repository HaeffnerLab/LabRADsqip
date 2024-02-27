from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit

class advanceDACs(pulse_sequence):
    required_parameters= [('DACcontrol','dac_pulse_length'),
#                          ('DACcontrol','U2target'),
                          ('DACcontrol','num_steps'),
                          ('DACcontrol','time_up'),
                          ('DACcontrol','wait_time')
                          ];
    def configuration(self):
        config = [
                  ('DACcontrol','dac_pulse_length'),
                  ('DACcontrol','U2target'),
                  ]
        return config
    
    def sequence(self):
        p = self.parameters.DACcontrol
        #print self.start, p.U2target
        print(p.items())
        self.end = self.start + p.time_up +p.wait_time 
        i = 0
        while i<p.num_steps:
            self.addTTL('adv', self.start+1.0*(i)/(p.num_steps)*p.time_up, p.dac_pulse_length )
            i = i+1
        print i
            