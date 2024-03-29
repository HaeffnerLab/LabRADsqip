from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from subsequences.RepumpDwithDoppler import doppler_cooling_after_repump_d
from subsequences.EmptySequence import empty_sequence
from subsequences.OpticalPumping import optical_pumping
from subsequences.RabiExcitation import rabi_excitation_select_channel
from subsequences.Tomography import tomography_readout
from subsequences.TurnOffAll import turn_off_all
from subsequences.SidebandCooling import sideband_cooling
from subsequences.voltage_ramp import ramp_voltage_up
from subsequences.reset_dac import reset_dac
from labrad.units import WithUnit
from treedict import TreeDict

class spectrum_rabi_with_multipole_ramp(pulse_sequence):
    
    required_parameters = [ 
                           ('Heating', 'background_heating_time'),
                           ('OpticalPumping','optical_pumping_enable'), 
                           ('SidebandCooling','sideband_cooling_enable'),
                           ]
    
    required_subsequences = [doppler_cooling_after_repump_d, empty_sequence, optical_pumping, 
                             rabi_excitation_select_channel, tomography_readout, turn_off_all, sideband_cooling, ramp_voltage_up, reset_dac]
    
    replaced_parameters = {empty_sequence:[('EmptySequence','empty_sequence_duration'),]}

    def sequence(self):
        p = self.parameters
        self.end = WithUnit(10, 'us')
        self.addSequence(turn_off_all)
        self.addSequence(doppler_cooling_after_repump_d)
        if p.OpticalPumping.optical_pumping_enable:
            self.addSequence(optical_pumping)
        if p.SidebandCooling.sideband_cooling_enable:
            self.addSequence(sideband_cooling)
            
         ################3   
        self.addSequence(ramp_voltage_up)
        ###############33
        self.addSequence(empty_sequence, TreeDict.fromdict({'EmptySequence.empty_sequence_duration':p.Heating.background_heating_time}))
        self.addSequence(rabi_excitation_select_channel)
        
        
        
        #############
        self.addSequence(reset_dac)
        ##############
        
        #print self.parameters.Excitation_729.rabi_excitation_frequency
        #import IPython
        #IPython.embed()
        
        self.addSequence(tomography_readout)