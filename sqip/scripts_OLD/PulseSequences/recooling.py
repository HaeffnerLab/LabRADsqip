from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from subsequences.TurnOffAll import turn_off_all
from subsequences.DopplerCooling import doppler_cooling
from subsequences.EmptySequence import empty_sequence
from subsequences.StateReadout import state_readout
from labrad.units import WithUnit
from treedict import TreeDict

class recooling(pulse_sequence):
    
    required_parameters =  [              
                            ('DopplerCooling', 'doppler_cooling_frequency_397'),
                            ('DopplerCooling', 'doppler_cooling_amplitude_397'),
                            ('DopplerCooling', 'doppler_cooling_frequency_866'),
                            ('DopplerCooling', 'doppler_cooling_amplitude_866'),
                            ('DopplerCooling', 'doppler_cooling_repump_additional'),
                            ('DopplerCooling', 'doppler_cooling_duration'),
                                      
                            ('StateReadout','state_readout_frequency_397'),
                            ('StateReadout','state_readout_amplitude_397'),
                            ('StateReadout','state_readout_frequency_866'),
                            ('StateReadout','state_readout_amplitude_866'),
                            ('StateReadout','state_readout_duration'),
                            ('StateReadout','use_camera_for_readout'),
                            
                            ('Recooling', 'cooling_off_duration'),
                           ]  

    required_subsequences = [turn_off_all, doppler_cooling, empty_sequence, state_readout]

    def sequence(self):
        p = self.parameters
        self.end = WithUnit(10, 'us')
        self.addSequence(turn_off_all)
        self.addSequence(doppler_cooling)
        self.start_record_timetags = self.end
        self.addSequence(empty_sequence, TreeDict.fromdict({'EmptySequence.empty_sequence_duration':p.Recooling.cooling_off_duration}))
        self.addSequence(state_readout)

        #record timetags the whole time
        self.timetag_record_duration = self.end - self.start_record_timetags
        self.addTTL('TimeResolvedCount', self.start_record_timetags, self.timetag_record_duration)

    
