from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from subsequences.RepumpDwithDoppler import doppler_cooling_after_repump_d
from subsequences.OpticalPumping import optical_pumping
from subsequences.RabiExcitation import rabi_excitation_select_channel
from subsequences.Tomography import tomography_readout
from subsequences.TurnOffAll import turn_off_all
from subsequences.SidebandCooling import sideband_cooling
from subsequences.reset_dac import reset_dac
from subsequences.ramp_wait_back_subsequence import ramp_wait_back
from labrad.units import WithUnit
from treedict import TreeDict
import labrad
import numpy

class spectrum_rabi_with_multipole_ramp(pulse_sequence):
    
    required_parameters = [ 
                           ('Heating', 'background_heating_time'),
                           ('OpticalPumping','optical_pumping_enable'), 
                           ('SidebandCooling','sideband_cooling_enable'),
                           ]
    
    required_subsequences = [doppler_cooling_after_repump_d,  optical_pumping, 
                             rabi_excitation_select_channel, tomography_readout, turn_off_all, sideband_cooling,ramp_wait_back,reset_dac]
    

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
        self.addSequence(ramp_wait_back)
        ###############33
        self.addSequence(rabi_excitation_select_channel)
        
        
        
        #############
        
        ##############
        
        #print self.parameters.Excitation_729.rabi_excitation_frequency
        #import IPython
        #IPython.embed()
        
        self.addSequence(tomography_readout)
	self.addSequence(reset_dac)
	
#Putting this here gets ''please create new sequence first''       
        '''def plot_current_sequence(cxn):
            from common.okfpgaservers.pulser.pulse_sequences.plot_sequence import SequencePlotter
            dds = cxn.pulser.human_readable_dds()
            ttl = cxn.pulser.human_readable_ttl()
            channels = numpy.asarray(cxn.pulser.get_channels())
            sp = SequencePlotter(ttl.asarray, dds.aslist, channels)
            sp.makePlot()
        plot_current_sequence(labrad.connect())'''
