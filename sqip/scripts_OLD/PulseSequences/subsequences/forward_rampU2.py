from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence

class forward_ramp_U2(pulse_sequence):
    def configuration(self):
        config = [
                  ('DACcontrol','dac_pulse_length'),
                  ('DACcontrol','num_steps'),
                  ('DACcontrol','time_down'),
                  ]
        return config
    
    def sequence(self):
        
        self.end = self.start + self.p.dac_pulse_length
        # N TTL pulses
        index = 1.0 
        while index <= (self.p.num_steps+1):
            self.ttl_pulses.append(('adv', self.start+self.p.time_down * (index-1), self.p.dac_pulse_length))
            index = index + 1
            
        
