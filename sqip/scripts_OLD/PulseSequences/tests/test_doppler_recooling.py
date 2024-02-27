from labrad.units import WithUnit
from common.okfpgaservers.pulser.pulse_sequences.plot_sequence import SequencePlotter
from sqip.scripts.PulseSequences.recooling import recooling

class test_parameters(object):
    
    parameters = {            
              ('DopplerCooling', 'doppler_cooling_frequency_397'):WithUnit(200.0, 'MHz'),
              ('DopplerCooling', 'doppler_cooling_amplitude_397'):WithUnit(-27.0, 'dBm'),
              ('DopplerCooling', 'doppler_cooling_frequency_866'):WithUnit(80.0, 'MHz'),
              ('DopplerCooling', 'doppler_cooling_amplitude_866'):WithUnit(-11.0, 'dBm'),
              ('DopplerCooling', 'doppler_cooling_repump_additional'):WithUnit(40, 'ns'),
              ('DopplerCooling', 'doppler_cooling_duration'):WithUnit(1.0,'ms'),
       
              ('Recooling','cooling_off_duration'):WithUnit(1.0, 'ms'),
              
              ('StateReadout','state_readout_frequency_397'):WithUnit(200.0, 'MHz'),
              ('StateReadout','state_readout_amplitude_397'):WithUnit(-10.0, 'dBm'),
              ('StateReadout','state_readout_frequency_866'):WithUnit(80.0, 'MHz'),
              ('StateReadout','state_readout_amplitude_866'):WithUnit(-11.0, 'dBm'),
              ('StateReadout','state_readout_duration'):WithUnit(0.25,'ms'),
              ('StateReadout','use_camera_for_readout'):False,

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
    cs = recooling(d)
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