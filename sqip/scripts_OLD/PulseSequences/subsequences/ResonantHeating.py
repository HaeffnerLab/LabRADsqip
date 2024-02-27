from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from sqip.scripts.PulseSequences.subsequences.DopplerCooling import doppler_cooling

class resonant_heating(pulse_sequence):
    
    required_parameters = [
                            ('Heating','resonant_heating_frequency_397'), 
                            ('Heating','resonant_heating_amplitude_397'), 
                            ('Heating','resonant_heating_frequency_866'), 
                            ('Heating','resonant_heating_amplitude_866'), 
                            ('Heating','resonant_heating_duration'),
                            ('Heating','resonant_heating_repump_additional')
                          ]
    
    required_subsequences = [doppler_cooling]
    
    def sequence(self):
        h = self.parameters.Heating
        repump_duration = h.resonant_heating_duration + h.resonant_heating_repump_additional
        self.addDDS('397DP',self.start, h.resonant_heating_duration, h.resonant_heating_frequency_397, h.resonant_heating_amplitude_397)
        if h.resonant_heating_duration['s'] > 40e-9:
            self.addTTL ('Optical4', self.start, h.resonant_heating_duration)
        self.addDDS ('866DP',self.start, repump_duration, h.resonant_heating_frequency_866, h.resonant_heating_amplitude_866)
        self.end = self.start + repump_duration
        
