from common.devel.bum.sequences.pulse_sequence import pulse_sequence
#from pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U
from treedict import TreeDict
import numpy as np




#class RabiFloppingMulti(pulse_sequence):
#    is_multi = True
#    sequences = [RabiFlopping, Spectrum]

class RabiFlopping(pulse_sequence):
    scannable_params = {
        'RabiFlopping.duration':  [(0., 60., 2., 'us'), 'rabi'],
        # 'Excitation_729.rabi_excitation_frequency':  [(-30., 30., 10., 'MHz'), 'spectrum'],
        'DopplerCooling.doppler_cooling_frequency_397':  [(200., 210., .5, 'MHz'), 'current'],
        'DopplerCooling.doppler_cooling_amplitude_397':  [(-30., -15., .5, 'dBm'), 'current'],
        'DopplerCooling.doppler_cooling_frequency_866':  [(80., 100., .5, 'MHz'), 'current'],
        'DopplerCooling.doppler_cooling_amplitude_866':  [(-20., -6., .5, 'dBm'), 'current'],

        'OpticalPumping.optical_pumping_amplitude_729':  [(-20., -6., .5, 'dBm'), 'current'],
        'OpticalPumping.optical_pumping_amplitude_854':  [(-20., -6., .5, 'dBm'), 'current'],
        'OpticalPumping.optical_pumping_amplitude_866':  [(-20., -6., .5, 'dBm'), 'current'],
        'OpticalPumping.optical_pumping_frequency_854':  [(85., 95., .5, 'MHz'), 'current'],
        'OpticalPumping.optical_pumping_frequency_866':  [(85., 95., .5, 'MHz'), 'current'],
        #'OpticalPumpingPulsed.optical_pumping_pulsed_duration_729': [(5., 50., 1,'us'),'current']       

        #'RabiFlopping.duration':  [(0., 50., 3, 'us'), 'rabi']
        #'Excitation_729.rabi_excitation_duration' : [(-150, 150, 10, 'MHz'),'spectrum'],
              }

    show_params= ['RabiFlopping.line_selection',
                  'RabiFlopping.rabi_amplitude_729',
                  'RabiFlopping.duration',
#                  'RabiFlopping.line_selection',
                 # 'RabiFlopping.selection_sideband',
                  'RabiFlopping.sideband_selection', ### this is the parameter we have, and we choose the order for each sideband. 
                 # 'RabiFlopping.order',
                 'StatePreparation.channel_729',
                  'Excitation_729.channel_729',
                  'OpticalPumpingPulsed.optical_pumping_pulsed_duration_729',
                  'OpticalPumpingPulsed.optical_pumping_pulsed_cycles',
                  'SidebadCooling'
                  ]
    
    #fixed_params = {'StateReadout.ReadoutMode':'camera'}



    def sequence(self):
      from StatePreparation import StatePreparation
      from subsequences.RabiExcitation import RabiExcitation
      from subsequences.StateReadout import StateReadout
      from subsequences.TurnOffAll import TurnOffAll
        
        ## calculate the scan params
      rf = self.parameters.RabiFlopping 
        
      # freq_729=self.calc_freq(rf.line_selection)   
        #freq_729=self.calc_freq(rf.line_selection , rf.sideband_selection[] , rf.order)
        # req_729=self.calc_freq(rf.line_selection , sideband , order)
      print "RabiFlopping line selection", rf
      freq_729=self.calc_freq_from_array(rf.line_selection, rf.sideband_selection)
        
        #print "Rabi flopping 729 freq is {}".format(freq_729)
        #print "Rabi flopping duration is {}".format(rf.duration)
        # building the sequence
      self.end = U(10., 'us')
      self.addSequence(TurnOffAll)
      self.addSequence(StatePreparation)
      self.addSequence(RabiExcitation,{  'Excitation_729.rabi_excitation_frequency': freq_729,
                                         'Excitation_729.rabi_excitation_amplitude': rf.rabi_amplitude_729,
                                         'Excitation_729.rabi_excitation_duration':  rf.duration })
      self.addSequence(StateReadout)
        
    @classmethod
    def run_initial(cls,cxn, parameters_dict):
	cxn.normalpmtflow.set_mode("Normal")
        pass

    @classmethod
    def run_in_loop(cls,cxn, parameters_dict, data, x):
        #print "Running in loop Rabi_floping"
        pass

    @classmethod
    def run_finally(cls,cxn, parameters_dict, data, x):
	cxn.normalpmtflow.set_mode("Differential")
        pass
        # print "switching the 866 back to ON"
        # cxn.pulser.switch_manual('866DP', True)
        #cxn.pulser.switch_manual('866DP', False)

        #np.save('temp_PMT', data)
        #print "saved ion data"
        
