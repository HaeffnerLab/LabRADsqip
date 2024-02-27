from common.devel.bum.sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit
#from OpticalPumpingContinuous import optical_pumping_continuous
#from treedict import TreeDict

class SidebandCooling(pulse_sequence):
    '''
    Single step of side band cooling DOES NOT include the optical pumping usually required
    paramters:
    duration
    729- choose carrier transition and sideband
    729- channel, amp, ac stark shift
    854- freq, amp
    866- freq, amp
    '''
    
    def sequence(self):
        
        sc = self.parameters.SidebandCooling
        sc2 = self.parameters.SequentialSBCooling
        scc = self.parameters.SidebandCoolingContinuous
        scp = self.parameters.SidebandCoolingPulsed
        op=self.parameters.OpticalPumping
        opc = self.parameters.OpticalPumpingContinuous
                              
        freq_729=self.calc_freq_from_array(sc.line_selection, sc.sideband_selection)
        freq_729 = freq_729 + sc.stark_shift
        print "SIDEBAND cooling 729 freq:.{}".format(freq_729)

        if sc.sideband_cooling_type == 'continuous':
            continuous = True
        elif sc.sideband_cooling_type == 'pulsed':
            continuous = False
        else:
            raise Exception ("Incorrect Sideband cooling type {0}".format(sc.sideband_cooling_type))
        
        freq_854 = sc.sideband_cooling_frequency_854
        freq_866 = sc.sideband_cooling_frequency_866
        ampl_854 = sc.sideband_cooling_amplitude_854
        ampl_729 = sc.sideband_cooling_amplitude_729
        ampl_866 = sc.sideband_cooling_amplitude_866

        self.end = self.start

        if continuous:
            duration = scc.sideband_cooling_continuous_duration
            for i in range(int(sc.sideband_cooling_cycles)):
                duration +=  sc.sideband_cooling_duration_729_increment_per_cycle
                dur_854 = duration + opc.optical_pumping_continuous_repump_additional
                dur_866 = duration + 2 * opc.optical_pumping_continuous_repump_additional
                self.addDDS('729DP', self.end, duration, freq_729, ampl_729)
                self.addDDS('854DP', self.end, dur_854, freq_854, ampl_854)
                self.addDDS('866DP', self.end, dur_866, freq_866, ampl_866)
                self.end += repump_dur_866

                repump_dur_854 = opc.optical_pumping_continuous_duration + opc.optical_pumping_continuous_repump_additional
                repump_dur_866 = opc.optical_pumping_continuous_duration + 2 * opc.optical_pumping_continuous_repump_additional
                self.addDDS('729DP', self.end, opc.optical_pumping_continuous_duration, freq_729, op.optical_pumping_amplitude_729)
                self.addDDS('854DP', self.end, repump_dur_854, op.optical_pumping_frequency_854, op.optical_pumping_amplitude_854)
                self.addDDS('866DP', self.end, repump_dur_866, op.optical_pumping_frequency_866, op.optical_pumping_amplitude_866)
                self.end = self.start + repump_dur_866
                if sc2.enable:
#         else:
#             duration = scp.sideband_cooling_pulsed_duration_729
        
        
#         channel_729 = self.parameters.StatePreparation.channel_729
        
#         repump_additional = self.parameters.OpticalPumpingContinuous.optical_pumping_continuous_repump_additional # need this for the additional repumper times
        
#         #Setting times
#         duration=self.parameters.SidebandCoolingContinuous.sideband_cooling_continuous_duration
#         repump_dur_854 = duration+ repump_additional
#         repump_dur_866 = duration + 2 * repump_additional
# #         
# #         print "Sideband Cooling", sc.line_selection
# #         print "freq 729:  ", channel_729
# #         print "freq 729:  ", channel_729
# #         print "freq 729:  ", freq_729        
     
#         self.addDDS(channel_729, self.start, duration, freq_729 , sc.sideband_cooling_amplitude_729)
#         self.addDDS('854DP',       self.start, repump_dur_854, sc.sideband_cooling_frequency_854 , sc.sideband_cooling_amplitude_854)
#         self.addDDS('866DP',       self.start, repump_dur_866, sc.sideband_cooling_frequency_866 , sc.sideband_cooling_amplitude_866)
#         # changing the 866 from a dds to a rf source enabled by a switch
#         self.end = self.start + repump_dur_866