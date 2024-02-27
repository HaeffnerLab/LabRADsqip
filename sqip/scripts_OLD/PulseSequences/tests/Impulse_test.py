from labrad.units import WithUnit
from common.okfpgaservers.pulser.pulse_sequences.plot_sequence import SequencePlotter
from sqip.scripts.PulseSequences.fast_change_impulse import fast_change_impulse


class test_parameters(object):
    
    parameters = {
                  
              ('DACcontrol','U2target'):5,
              ('DACcontrol','enable_ramp'):True,
              ('DACcontrol','num_steps'):125,
              ('DACcontrol','time_down'):WithUnit(2, 'ms'),
              ('DACcontrol','time_up'):WithUnit(10, 'ms'),
              ('DACcontrol','wait_time'):WithUnit(200, 'ms'),
              ('DACcontrol','dac_pulse_length'):WithUnit(.1, 'us'),
 #             ('DACcontrol','dac_pulse_length'):WithUnit(.05, 's'),
            
              ('RepumpD_5_2','repump_d_duration'):WithUnit(200, 'us'),
              ('RepumpD_5_2','repump_d_frequency_854'):WithUnit(80.0, 'MHz'),
              ('RepumpD_5_2','repump_d_amplitude_854'):WithUnit(-11.0, 'dBm'),
              
              ('DopplerCooling', 'doppler_cooling_frequency_397'):WithUnit(200.0, 'MHz'),
              ('DopplerCooling', 'doppler_cooling_amplitude_397'):WithUnit(-15.0, 'dBm'),
              ('DopplerCooling', 'doppler_cooling_frequency_866'):WithUnit(80.0, 'MHz'),
              ('DopplerCooling', 'doppler_cooling_amplitude_866'):WithUnit(-11.0, 'dBm'),
              ('DopplerCooling', 'doppler_cooling_repump_additional'):WithUnit(100, 'us'),
              ('DopplerCooling', 'doppler_cooling_duration'):WithUnit(1.0,'ms'),
              
              ('OpticalPumping','optical_pumping_enable'):True,
              ('OpticalPumping','optical_pumping_frequency_729'):WithUnit(0.0, 'MHz'),
              ('OpticalPumping','optical_pumping_frequency_854'):WithUnit(80.0, 'MHz'),
              ('OpticalPumping','optical_pumping_frequency_866'):WithUnit(80.0, 'MHz'),
              ('OpticalPumping','optical_pumping_amplitude_729'):WithUnit(-10.0, 'dBm'),
              ('OpticalPumping','optical_pumping_amplitude_854'):WithUnit(-3.0, 'dBm'),
              ('OpticalPumping','optical_pumping_amplitude_866'):WithUnit(-11.0, 'dBm'),
              ('OpticalPumping','optical_pumping_type'):'continuous',
              
              ('OpticalPumpingContinuous','optical_pumping_continuous_duration'):WithUnit(1, 'ms'),
              ('OpticalPumpingContinuous','optical_pumping_continuous_repump_additional'):WithUnit(200, 'us'),
              
              ('OpticalPumpingPulsed','optical_pumping_pulsed_cycles'):2.0,
              ('OpticalPumpingPulsed','optical_pumping_pulsed_duration_729'):WithUnit(20, 'us'),
              ('OpticalPumpingPulsed','optical_pumping_pulsed_duration_repumps'):WithUnit(20, 'us'),
              ('OpticalPumpingPulsed','optical_pumping_pulsed_duration_additional_866'):WithUnit(20, 'us'),
              ('OpticalPumpingPulsed','optical_pumping_pulsed_duration_between_pulses'):WithUnit(5, 'us'),

              ('SidebandCooling','sideband_cooling_enable'):True,
              ('SidebandCooling','sideband_cooling_cycles'): 4.0,
              ('SidebandCooling','sideband_cooling_type'):'continuous',
              ('SidebandCooling','sideband_cooling_duration_729_increment_per_cycle'):WithUnit(0, 'us'),
              ('SidebandCooling','sideband_cooling_frequency_854'):WithUnit(80.0, 'MHz'),
              ('SidebandCooling','sideband_cooling_amplitude_854'):WithUnit(-11.0, 'dBm'),
              ('SidebandCooling','sideband_cooling_frequency_866'):WithUnit(80.0, 'MHz'),
              ('SidebandCooling','sideband_cooling_amplitude_866'):WithUnit(-11.0, 'dBm'),
              ('SidebandCooling','sideband_cooling_frequency_729'):WithUnit(-10.0, 'MHz'),
              ('SidebandCooling','sideband_cooling_amplitude_729'):WithUnit(-11.0, 'dBm'),
              ('SidebandCooling','sideband_cooling_optical_pumping_duration'):WithUnit(500, 'us'),
              
              ('SidebandCoolingContinuous','sideband_cooling_continuous_duration'):WithUnit(500, 'us'),
              
              ('SidebandCoolingPulsed','sideband_cooling_pulsed_duration_729'):WithUnit(10, 'us'),
              ('SidebandCoolingPulsed','sideband_cooling_pulsed_cycles'):10.0,
              ('SidebandCoolingPulsed','sideband_cooling_pulsed_duration_repumps'):WithUnit(10, 'us'),
              ('SidebandCoolingPulsed','sideband_cooling_pulsed_duration_additional_866'):WithUnit(10, 'us'),
              ('SidebandCoolingPulsed','sideband_cooling_pulsed_duration_between_pulses'):WithUnit(5, 'us'),
       
              ('Heating','background_heating_time'):WithUnit(0.0, 'ms'),
              
              ('Excitation_729','rabi_excitation_frequency'):WithUnit(10.0, 'MHz'),
              ('Excitation_729','rabi_excitation_amplitude'):WithUnit(-3.0, 'dBm'),
              ('Excitation_729','rabi_excitation_duration'):WithUnit(10.0, 'us'),
              ('Excitation_729','rabi_excitation_phase'):WithUnit(0.0, 'deg'),
              
              ('StateReadout','state_readout_frequency_397'):WithUnit(200.0, 'MHz'),
              ('StateReadout','state_readout_amplitude_397'):WithUnit(-13.0, 'dBm'),
              ('StateReadout','state_readout_frequency_866'):WithUnit(80.0, 'MHz'),
              ('StateReadout','state_readout_amplitude_866'):WithUnit(-11.0, 'dBm'),
              ('StateReadout','state_readout_duration'):WithUnit(3.0,'ms'),
              ('StateReadout','use_camera_for_readout'):False,
                  
              ('Tomography', 'rabi_pi_time'):WithUnit(50.0, 'us'),
              ('Tomography', 'iteration'):0,
              ('Tomography', 'tomography_excitation_frequency'):WithUnit(0.0, 'MHz'),
              ('Tomography', 'tomography_excitation_amplitude'):WithUnit(-11.0, 'dBm'),
              }

def main():
    import labrad
    cxn = labrad.connect()
    import time
    from treedict import TreeDict
    cxn.pulser.switch_auto('adv',True)
    cxn.pulser.switch_auto('rst',True)
    #cxn.pulser.switch_auto('adv')
    #cxn.pulser.switch_auto('rst')
    params = test_parameters.parameters
    d = TreeDict()
    #make a treedictionary out of the parameters
    for (collection,param), value in test_parameters.parameters.iteritems():
        d['{0}.{1}'.format(collection, param)] = value

    tinit = time.time()
    cs = fast_change_impulse(d)
    cs.programSequence(cxn.pulser)
    print 'to program', time.time() - tinit
    cxn.pulser.start_number(140)
    cxn.pulser.wait_sequence_done()
    cxn.pulser.stop_sequence()
    cxn.pulser.switch_auto('adv',False)
    cxn.pulser.switch_auto('rst',False)
    cxn.pulser.switch_manual('adv',True)
    cxn.pulser.switch_manual('adv',False)
    
if __name__ == '__main__':
        main()