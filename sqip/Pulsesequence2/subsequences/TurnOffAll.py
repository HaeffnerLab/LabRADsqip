from common.devel.bum.sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit

class TurnOffAll(pulse_sequence):
    
    def sequence(self):
        dur = WithUnit(50, 'us')
        for channel in ['729DP','397DP','854DP','866DP']:
            self.addDDS(channel, self.start, dur, WithUnit(0, 'MHz'), WithUnit(-63., 'dBm') )
#        self.addTTL('866DP', self.start, dur )

        self.end = self.start + dur
