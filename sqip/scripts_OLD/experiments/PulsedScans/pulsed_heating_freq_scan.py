from common.abstractdevices.script_scanner.scan_methods import experiment
from test_pulsed_heating import pulsed_heating
from sqip.scripts.scriptLibrary.common_methods_729 import common_methods_729 as cm
from sqip.scripts.scriptLibrary import dvParameters
import time
import labrad
from labrad.units import WithUnit
from numpy import linspace

class pulsed_heating_freq_scan(experiment):
    
    name = 'PulsedHeatingFreqScan'
    trap_frequencies = [
                        ('TrapFrequencies','axial_frequency'),
                        ('TrapFrequencies','radial_frequency_1'),
                        ('TrapFrequencies','radial_frequency_2'),
                        ('TrapFrequencies','rf_drive_frequency'),                       
                        ]
    required_parameters = [
                           ('Heating', 'scan_pulse_freq'),
                           ('Heating', 'enable_kicking'),
                           ]
    required_parameters.extend(trap_frequencies)
    optional_parmeters = [
                          ('PulsedHeating', 'window_name')
                          ]
    required_parameters.extend(pulsed_heating.required_parameters)
    #removing parameters we'll be overwriting, and they do not need to be loaded   
    #required_parameters.remove(('Heating','coherent_evolution_time'))
    
    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.kick = self.make_experiment(pulsed_heating)
        self.kick.initialize(cxn, context, ident)
        self.scan = []
        self.amplitude = None
        self.duration = None
        self.cxnlab = labrad.connect('192.168.169.49') #connection to labwide network
        self.drift_tracker = cxn.sd_tracker
        self.square_pulse_generator = cxn.rigol_dg4062_server
        self.square_pulse_generator.select_device('sqip_expcontrol GPIB Bus - USB0::0x1AB1::0x0641::DG4D152500738')
        self.init_pulsing_freq = self.square_pulse_generator.frequency()
        self.init_pulsing_state = self.square_pulse_generator.output()
        self.square_pulse_generator.burst_mode('gated')
        self.square_pulse_generator.burst_state(True)
        if self.parameters.Heating.enable_kicking:
            self.square_pulse_generator.output(True)
        self.dv = cxn.data_vault
        self.pulsed_heating_save_context = cxn.context()
    
    def setup_sequence_parameters(self):
        self.load_frequency()
        pulse = self.parameters.PulsedHeat
        print self.parameters.PulsedHeat.items()
        minim,maxim,steps = self.parameters.Heating.scan_pulse_freq
        minim = minim['MHz']; maxim = maxim['MHz']
        self.scan = linspace(minim,maxim, steps)
        self.scan = [WithUnit(pt, 'MHz') for pt in self.scan]
        
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
        window_name = self.parameters.get('PulsedHeatingFreqScan.window_name', ['Pulsed Heating Frequency Scan'])
        self.dv.add_parameter('Window', window_name, context = self.pulsed_heating_save_context)
        self.dv.add_parameter('plotLive', True, context = self.pulsed_heating_save_context)
    
    def load_frequency(self):
        #reloads trap frequencyies and gets the latest information from the drift tracker
        self.reload_some_parameters(self.trap_frequencies) 
        
    def run(self, cxn, context):
        self.setup_data_vault()
        self.setup_sequence_parameters()
        for i,freq in enumerate(self.scan):
            print 'running', freq
            should_stop = self.pause_or_stop()
            if should_stop: break
            self.load_frequency()
            self.kick.set_parameters(self.parameters)
            self.square_pulse_generator.frequency(freq)
            kicking = self.kick.run(cxn, context)
            submission = [freq['MHz']]
            submission.append(kicking)
            print submission
            self.dv.add(submission, context = self.pulsed_heating_save_context)
            self.update_progress(i)
     
    def finalize(self, cxn, context):
        self.save_parameters(self.dv, cxn, self.cxnlab, self.pulsed_heating_save_context)
        self.square_pulse_generator.frequency(self.init_pulsing_freq)
        self.square_pulse_generator.output(self.init_pulsing_state)
        
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
    exprt = pulsed_heating_freq_scan(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)