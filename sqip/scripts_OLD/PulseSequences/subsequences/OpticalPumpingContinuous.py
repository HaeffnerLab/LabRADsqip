from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit

class optical_pumping_continuous(pulse_sequence):
    
    
    required_parameters = [
                  ('OpticalPumpingContinuous','optical_pumping_continuous_duration'),
                  ('OpticalPumpingContinuous','optical_pumping_continuous_repump_additional'),
                  ('OpticalPumpingContinuous','optical_pumping_continuous_frequency_854'),
                  ('OpticalPumpingContinuous','optical_pumping_continuous_amplitude_854'),
                  ('OpticalPumpingContinuous','optical_pumping_continuous_frequency_729'),
                  ('OpticalPumpingContinuous','optical_pumping_continuous_amplitude_729'),
                  ('OpticalPumpingContinuous','optical_pumping_continuous_frequency_866'), 
                  ('OpticalPumpingContinuous','optical_pumping_continuous_amplitude_866'),
                  ('Globals','Offset729'),
                  ]

    def sequence(self):
        opc = self.parameters.OpticalPumpingContinuous
        glo = self.parameters.Globals # Added by Maya 1/2015
        repump_dur_854 = opc.optical_pumping_continuous_duration + opc.optical_pumping_continuous_repump_additional
        repump_dur_866 = opc.optical_pumping_continuous_duration + 2 * opc.optical_pumping_continuous_repump_additional
        self.end = self.start + repump_dur_866
       
        #self.addTTL(('854DP',self.start + WithUnit(0.04, 'us'), repump_dur_854 - WithUnit(0.04, 'us'))) 
        #self.addDDS('729', self.start, opc.optical_pumping_continuous_duration, opc.optical_pumping_continuous_frequency_729, opc.optical_pumping_continuous_amplitude_729)
        self.addDDS('729', self.start, opc.optical_pumping_continuous_duration, opc.optical_pumping_continuous_frequency_729, opc.optical_pumping_continuous_amplitude_729 + glo.Offset729)        
        self.addDDS('854', self.start, repump_dur_854, opc.optical_pumping_continuous_frequency_854, opc.optical_pumping_continuous_amplitude_854)
        self.addDDS('866', self.start, repump_dur_866, opc.optical_pumping_continuous_frequency_866, opc.optical_pumping_continuous_amplitude_866)