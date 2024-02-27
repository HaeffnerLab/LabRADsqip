from common.abstractdevices.script_scanner.scan_methods import experiment
from test_pulsed_heating import pulsed_heating
from sqip.scripts.scriptLibrary.common_methods_729 import common_methods_729 as cm
from sqip.scripts.scriptLibrary import dvParameters
import time
import labrad
from labrad.units import WithUnit
from numpy import linspace

class pulsed_heating_scan(experiment):
    
    name = 'PulsedHeatingScan'
    trap_frequencies = [
                        ('TrapFrequencies','axial_frequency'),
                        ('TrapFrequencies','radial_frequency_1'),
                        ('TrapFrequencies','radial_frequency_2'),
                        ('TrapFrequencies','rf_drive_frequency'),                       
                        ]
    required_parameters = [
                           ('PulsedHeat','time_interval_scan'),
                           ]
    required_parameters.extend(trap_frequencies)
    optional_parmeters = [
                          ('PulsedHeating', 'window_name')
                          ]
    required_parameters.extend(pulsed_heating.required_parameters)
    #removing parameters we'll be overwriting, and they do not need to be loaded   
    
    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.kick = self.make_experiment(pulsed_heating)
        self.kick.initialize(cxn, context, ident)
        self.scan = []
        self.amplitude = None
        self.duration = None
        self.cxnlab = labrad.connect('192.168.169.49') #connection to labwide network
        self.drift_tracker = cxn.sd_tracker
        self.dv = cxn.data_vault
        self.pulsed_heating_save_context = cxn.context()
    
    def setup_sequence_parameters(self):
        self.load_frequency()
        pulse = self.parameters.PulsedHeat
        print pulse.time_interval_scan
        minim,maxim,steps = pulse.time_interval_scan
        minim = minim['us']; maxim = maxim['us']
        self.scan = linspace(minim,maxim, steps)
        self.scan = [WithUnit(pt, 'us') for pt in self.scan]
        
    def setup_data_vault(self):
        localtime = time.localtime()
        datasetNameAppend = time.strftime("%Y%b%d_%H%M_%S",localtime)
        dirappend = [ time.strftime("%Y%b%d",localtime) ,time.strftime("%H%M_%S", localtime)]
        directory = ['','Experiments']
        directory.extend([self.name])
        directory.extend(dirappend)
        self.dv.cd(directory ,True, context = self.pulsed_heating_save_context)
        output_size = self.kick.output_size
        dependants = [('Excitation','Ion {}'.format(ion),'Probability') for ion in range(output_size)]
        self.dv.new('Pulsed Heating {}'.format(datasetNameAppend),[('Excitation', 'us')], dependants , context = self.pulsed_heating_save_context)
        window_name = self.parameters.get('PulsedHeating.window_name', ['Pulsed Heating'])
        self.dv.add_parameter('Window', window_name, context = self.pulsed_heating_save_context)
        self.dv.add_parameter('plotLive', True, context = self.pulsed_heating_save_context)
    
    def load_frequency(self):
        #reloads trap frequencyies and gets the latest information from the drift tracker
        self.reload_some_parameters(self.trap_frequencies) 
#        pulse = self.parameters.pulsed_heating_scan
#        frequency = cm.frequency_from_line_selection(pulse.frequency_selection, pulse.manual_frequency_729, pulse.line_selection, self.drift_tracker)
#        trap = self.parameters.TrapFrequencies
#        if pulse.frequency_selection == 'auto':
#            frequency = cm.add_sidebands(frequency, pulse.sideband_selection, trap)
#        self.parameters['Excitation_729.rabi_excitation_frequency'] = frequency
        
    def run(self, cxn, context):
        self.setup_data_vault()
        self.setup_sequence_parameters()
        for i,duration in enumerate(self.scan):
            print 'running', duration
            should_stop = self.pause_or_stop()
            if should_stop: break
            self.load_frequency()
            #self.parameters['Excitation_729.rabi_excitation_duration'] = duration
            self.kick.set_parameters(self.parameters)
            kicking = self.kick.run(cxn, context)
            submission = [duration['us']]
            submission.append(kicking)
            print submission
            self.dv.add(submission, context = self.pulsed_heating_save_context)
            self.update_progress(i)
     
    def finalize(self, cxn, context):
        self.save_parameters(self.dv, cxn, self.cxnlab, self.pulsed_heating_save_context)
        self.kick.finalize(cxn, context)

    def update_progress(self, iteration):
        progress = self.min_progress + (self.max_progress - self.min_progress) * float(iteration + 1.0) / len(self.scan)
        self.sc.script_set_progress(self.ident,  progress)

    def save_parameters(self, dv, cxn, cxnlab, context):
        measuredDict = dvParameters.measureParameters(cxn, cxnlab)
        dvParameters.saveParameters(dv, measuredDict, context)
        dvParameters.saveParameters(dv, dict(self.parameters), context)   

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = pulsed_heating_scan(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)