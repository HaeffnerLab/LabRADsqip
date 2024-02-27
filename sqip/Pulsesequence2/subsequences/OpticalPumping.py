from common.devel.bum.sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit

class OpticalPumping(pulse_sequence):
    
    '''
    Optical pumping unig a frequency selective transition  
    '''


    def sequence(self):
        op=self.parameters.OpticalPumping
        opc = self.parameters.OpticalPumpingContinuous
        opp = self.parameters.OpticalPumpingPulsed 
        # choose the carrier frequency
        freq_729=self.calc_freq_from_array(op.line_selection)
        # print "Optical pumping 729 freq:.{}".format(freq_729)        
        # print "Optical pumping line selection:.{}".format(op.line_selection)
        # print freq_729
        if op.optical_pumping_type == 'continuous':
            continuous = True
        elif op.optical_pumping_type == 'pulsed':
            continuous = False
        else:
            raise Exception ('Incorrect optical pumping type {0}'.format(op.optical_pumping_type))
        if continuous:
            # print "Optical pumping continuously"
            repump_dur_854 = opc.optical_pumping_continuous_duration + opc.optical_pumping_continuous_repump_additional
            repump_dur_866 = opc.optical_pumping_continuous_duration + 2 * opc.optical_pumping_continuous_repump_additional
            self.end = self.start + repump_dur_866
            
            self.addDDS('729DP', self.start, opc.optical_pumping_continuous_duration, freq_729, op.optical_pumping_amplitude_729)
            #print 'op:', opc.optical_pumping_continuous_frequency_729
            #print 'op:',  opc.optical_pumping_continuous_duration
            self.addDDS('854DP', self.start, repump_dur_854, op.optical_pumping_frequency_854, op.optical_pumping_amplitude_854)
            self.addDDS('866DP', self.start, repump_dur_866, op.optical_pumping_frequency_866, op.optical_pumping_amplitude_866)
            # changing the 866 from a dds to a rf source enabled by a switch
            #self.addTTL('866DP', self.start + WithUnit(0.25, 'us'), repump_dur_866 - WithUnit(0.1, 'us') )
            #aux = self.parameters.OpticalPumpingAux
            #if aux.aux_op_enable:
                #self.addDDS('729DP_aux', self.start, opc.optical_pumping_continuous_duration, aux.aux_optical_frequency_729, aux.aux_optical_pumping_amplitude_729)
                #print 'aux op:', aux.aux_optical_frequency_729
        else:
            # print "Optical pumping pulsed"
            cycles = int(opp.optical_pumping_pulsed_cycles)
            cycle_duration = opp.optical_pumping_pulsed_duration_729 + opp.optical_pumping_pulsed_duration_repumps + opp.optical_pumping_pulsed_duration_additional_866 + 2 * opp.optical_pumping_pulsed_duration_between_pulses
            cycles_start = [self.start + cycle_duration * i for i in range(cycles)]
            self.end = self.start + cycles * cycle_duration
            ampl729 = op.optical_pumping_amplitude_729
            freq866 = op.optical_pumping_frequency_866
            ampl866 = op.optical_pumping_amplitude_866
            freq854 = op.optical_pumping_frequency_854
            ampl854 = op.optical_pumping_amplitude_854
            for start in cycles_start:
                start_repumps = start + opp.optical_pumping_pulsed_duration_729 + opp.optical_pumping_pulsed_duration_between_pulses
                duration_866 =  opp.optical_pumping_pulsed_duration_repumps + opp.optical_pumping_pulsed_duration_additional_866
                self.addDDS('729DP', start, opp.optical_pumping_pulsed_duration_729 , freq_729 , ampl729)
                self.addDDS('854DP', start_repumps, opp.optical_pumping_pulsed_duration_repumps, freq854, ampl854)
                self.addDDS('866DP', start_repumps, duration_866, freq866 , ampl866)
