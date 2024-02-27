from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit

class resetDACs(pulse_sequence):
    required_parameters= [('DACcontrol','dac_pulse_length'),
                          ('DACcontrol','U2target')
                          ];
    def configuration(self):
        config = [
                  ('DACcontrol','dac_pulse_length'),
                  ]
        return config
    
    def sequence(self):
        p = self.parameters.DACcontrol
        self.end = self.start + 3*p.dac_pulse_length
        self.addTTL('rst', self.start, 3*p.dac_pulse_length )# self.p.dac_pulse_length
        self.addTTL('adv', self.start + p.dac_pulse_length,  p.dac_pulse_length )#self.p.dac_pulse_length   