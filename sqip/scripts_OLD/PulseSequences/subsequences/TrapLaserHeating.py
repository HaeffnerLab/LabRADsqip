from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from treedict import TreeDict

class trap_laser_heating(pulse_sequence):
    
    required_parameters = [
                             ('Heating','ontrap_laser_duration'), 
                             ('Heating','ontrap_laser_amplitude'),
                             ('Heating','ontrap_laser_frequency'), 
                          ]
        
    def sequence(self):
        h = self.parameters.Heating
        repump_duration = h.ontrap_laser_duration #+ h.resonant_heating_repump_additional
        self.addDDS('SPARE',self.start, h.ontrap_laser_duration, h.ontrap_laser_frequency, h.ontrap_laser_amplitude)
        if h.ontrap_laser_duration['s'] > 40e-9:
            self.addTTL ('Optical4', self.start, h.ontrap_laser_duration)
        #self.end = self.start + repump_duration
        self.end = self.start# + repump_duration # 0714
        
