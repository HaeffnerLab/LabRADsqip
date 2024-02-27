from labrad.units import WithUnit
from common.okfpgaservers.pulser.pulse_sequences.plot_sequence import SequencePlotter
from sqip.scripts.PulseSequences.kicked_coherent import kicked_coherent 

class test_parameters(object):
    
    parameters = {
              ('RepumpD_5_2','repump_d_duration'):WithUnit(200, 'us'),
              ('RepumpD_5_2','repump_d_frequency_854'):WithUnit(80.0, 'MHz'),
              ('RepumpD_5_2','repump_d_amplitude_854'):WithUnit(-11.0, 'dBm'),
              
              ('DopplerCooling', 'doppler_cooling_frequency_397'):WithUnit(200.0, 'MHz'),
              ('DopplerCooling', 'doppler_cooling_amplitude_397'):WithUnit(-26.0, 'dBm'),
              ('DopplerCooling', 'doppler_cooling_frequency_866'):WithUnit(80.0, 'MHz'),
              ('DopplerCooling', 'doppler_cooling_amplitude_866'):WithUnit(-33.0, 'dBm'),
              ('DopplerCooling', 'doppler_cooling_repump_additional'):WithUnit(40, 'ns'),
              ('DopplerCooling', 'doppler_cooling_duration'):WithUnit(1.0,'ms'),
              
              ('Heating', 'resonant_heating_duration'):WithUnit(100.,'us'),
              ('Heating', 'resonant_heating_repump_additional'):WithUnit(40.0,'ns'),
              ('Heating', 'resonant_heating_amplitude_397'):WithUnit(-5.0, 'dBm'),
              ('Heating', 'resonant_heating_frequency_397'):WithUnit(220.0, 'MHz'),
              ('Heating', 'resonant_heating_frequency_866'):WithUnit(80.0, 'MHz'),
              ('Heating', 'resonant_heating_amplitude_866'):WithUnit(-8.0, 'dBm'),
              ('Heating', 'coherent_evolution_time'):WithUnit(100.,'us'),
              
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

              ('SidebandCooling','sideband_cooling_enable'):False,
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
              
              ('SidebandCoolingContinuous','sideband_cooling_continuous_duration'):WithUnit(100, 'us'),
              
              ('SidebandCoolingPulsed','sideband_cooling_pulsed_duration_729'):WithUnit(10, 'us'),
              ('SidebandCoolingPulsed','sideband_cooling_pulsed_cycles'):10.0,
              ('SidebandCoolingPulsed','sideband_cooling_pulsed_duration_repumps'):WithUnit(10, 'us'),
              ('SidebandCoolingPulsed','sideband_cooling_pulsed_duration_additional_866'):WithUnit(10, 'us'),
              ('SidebandCoolingPulsed','sideband_cooling_pulsed_duration_between_pulses'):WithUnit(5, 'us'),
              
              ('StateReadout','state_readout_frequency_397'):WithUnit(200.0, 'MHz'),
              ('StateReadout','state_readout_amplitude_397'):WithUnit(-13.0, 'dBm'),
              ('StateReadout','state_readout_frequency_866'):WithUnit(80.0, 'MHz'),
              ('StateReadout','state_readout_amplitude_866'):WithUnit(-11.0, 'dBm'),
              ('StateReadout','state_readout_duration'):WithUnit(0.25,'ms'),
              ('StateReadout','use_camera_for_readout'):False,
                  
              ('Tomography', 'rabi_pi_time'):WithUnit(50.0, 'us'),
              ('Tomography', 'iteration'):1,
              ('Tomography', 'tomography_excitation_frequency'):WithUnit(0.0, 'MHz'),
              ('Tomography', 'tomography_excitation_amplitude'):WithUnit(-11.0, 'dBm'),
              }

if __name__ == '__main__':
    import labrad
    import time
    cxn = labrad.connect()
    from treedict import TreeDict
    params = test_parameters.parameters
    d = TreeDict()
    #make a treedictionary out of the parameters
    for (collection,param), value in test_parameters.parameters.iteritems():
        d['{0}.{1}'.format(collection, param)] = value
    tinit = time.time()
    cs = kicked_coherent(d)
    cs.programSequence(cxn.pulser)
    print 'to program', time.time() - tinit
    cxn.pulser.start_number(10)
    cxn.pulser.wait_sequence_done()
    cxn.pulser.stop_sequence()
    timetags = cxn.pulser.get_timetags().asarray
    print timetags
    readout = cxn.pulser.get_readout_counts().asarray
    print readout
    dds = cxn.pulser.human_readable_dds()
    ttl = cxn.pulser.human_readable_ttl()
    channels = cxn.pulser.get_channels().asarray
    sp = SequencePlotter(ttl.asarray, dds.aslist, channels)
    sp.makePlot()