from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence

class wait_for_heating(pulse_sequence):
    
    
    required_parameters =  [('Heating', 'background_heating_time')]

    def sequence(self):
        self.end = self.start + self.parameters.Heating.background_heating_time
