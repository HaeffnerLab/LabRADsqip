from common.devel.bum.sequences.pulse_sequence import pulse_sequence
#from pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U
from treedict import TreeDict
import numpy as np

class Ramsey(pulse_sequence):
    
    #name = 'Ramsey'

    scannable_params = {
                        
        'Ramsey.ramsey_time': [(0, 1.0, 0.05, 'ms') ,'ramsey'],
        'Ramsey.second_pulse_phase': [(0, 360., 15, 'deg') ,'ramsey']
        }

    show_params= ['Ramsey.ramsey_time',
                  # 'RamseyScanPhase.scanphase',
                  'Ramsey.detuning',
                  
                  #need to work on this
                  # 'GlobalRotation.amplitude',
                  # 'GlobalRotation.pi_time',
                  'RabiFlopping.rabi_amplitude_729',
                  'RabiFlopping.line_selection',
                  'RabiFlopping.sideband_selection',
                  'RabiFlopping.rabi_pi_time',

                  'StatePreparation.channel_729',
                  'StatePreparation.optical_pumping_enable',
                  'StatePreparation.sideband_cooling_enable']

    
    def sequence(self):
        
        from StatePreparation import StatePreparation
        from subsequences.RabiExcitation import RabiExcitation
        from subsequences.StateReadout import StateReadout
        from subsequences.EmptySequence import EmptySequence
        from subsequences.StateReadout import StateReadout
        
        
        
        ## calculate the 729 params
        rf = self.parameters.RabiFlopping   
        # calculating the 729 freq form the Rabi flop params
        freq_729=self.calc_freq_from_array(rf.line_selection , rf.sideband_selection)
        # adding the Ramsey detuning
        freq_729 = freq_729+ self.parameters.Ramsey.detuning
        pi_time = rf.rabi_pi_time
        wait_time = self.parameters.Ramsey.ramsey_time
        second_phase = self.parameters.Ramsey.second_pulse_phase

        
        print "1234"
        print " freq 729 " , freq_729
        print " Wait time ", wait_time
        
        # building the sequence
        self.addSequence(StatePreparation)            
        self.addSequence(RabiExcitation, { "Excitation_729.rabi_excitation_frequency":freq_729,
                                           "Excitation_729.rabi_excitation_duration":  0.5*pi_time,
                                           "Excitation_729.rabi_excitation_amplitude": rf.rabi_amplitude_729,
                                           "Excitation_729.rabi_excitation_phase": U(0, 'deg')
                                          })
        
        self.addSequence(EmptySequence,  { "EmptySequence.empty_sequence_duration" : wait_time})
        
        self.addSequence(RabiExcitation, { "Excitation_729.rabi_excitation_frequency":freq_729,
                                           "Excitation_729.rabi_excitation_duration":  0.5*pi_time,
                                           "Excitation_729.rabi_excitation_amplitude": rf.rabi_amplitude_729,
                                           "Excitation_729.rabi_excitation_phase": second_phase
                                          })
        self.addSequence(StateReadout)
        
    @classmethod
    def run_initial(cls,cxn, parameters_dict):
        pass
        
    @classmethod
    def run_in_loop(cls,cxn, parameters_dict, data, x):
        #print "Running in loop Rabi_floping"
        pass
    
    @classmethod
    def run_finally(cls,cxn, parameters_dict, data, x):
        pass

        

#if __name__=='__main__':
#    #pv = TreeDict.fromdict({'DopplerCooling.duration':U(5, 'us')})
    #ex = Sequence(pv)
    #psw = pulse_sequence_wrapper('example.xml', pv)
#    print 'executing a scan gap'
#    Ramsey.execute_external(('Ramsey.ramsey_time', 0, 10.0, 0.1, 'ms'))