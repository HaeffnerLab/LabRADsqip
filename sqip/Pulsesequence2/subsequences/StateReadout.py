from common.devel.bum.sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit
#from treedict import TreeDict

class StateReadout(pulse_sequence):
    '''
    Pulse sequence for reading out the state of the ion. 
    '''
    
    
    def sequence(self):
        
        st = self.parameters.StateReadout
        readout_mode = 'pmt'  #st.readout_mode
        repump_additional = self.parameters.DopplerCooling.doppler_cooling_repump_additional# need the doppler paramters for the additional repumper time 
        # print "readout repump_additional ",repump_additional 
        # st.use_camera_for_readout = False
        readout_duration=st.state_readout_duration
        # print " pmt_readout_duration ",readout_duration 
        duration_397=readout_duration
        duration_866=readout_duration + repump_additional
        
        
        self.addTTL('ReadoutCount', self.start, readout_duration)
        
        self.addDDS ('397DP',self.start, duration_397, st.state_readout_frequency_397, st.state_readout_amplitude_397)
        self.addDDS ('866DP',self.start, duration_866, st.state_readout_frequency_866, st.state_readout_amplitude_866)
        
        # changing the 866 from a dds to a rf source enabled by a switch
        #self.addTTL('866DP', self.start+ WithUnit(0.25, 'us'), duration_866 - WithUnit(0.1, 'us') )
                    
        self.end = self.start + duration_866
#         print "397 amp.{}".format(st.state_readout_amplitude_397)
        
