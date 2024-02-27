from sqip.scripts.experiments.Experiments729.rabi_flopping import rabi_flopping
import sqip.scripts.experiments.CalibrationScans.heatingRateAnalysis.sqip_rate_from_flops as fitter
from common.abstractdevices.script_scanner.scan_methods import experiment
from sqip.scripts.experiments.Experiments729.excitations import excitation_729
from sqip.scripts.scriptLibrary.common_methods_729 import common_methods_729 as cm
from sqip.scripts.scriptLibrary import dvParameters
from sqip.scripts.experiments.Crystallization.crystallization import crystallization
from sqip.scripts.scriptLibrary import scan_methods
import time
import labrad
from labrad.units import WithUnit
from numpy import linspace
from treedict import TreeDict
class rabi_flopping_scan_heatingtime(experiment):
    
    name = 'RabiFloppingScanHeatingTime'
    trap_frequencies = [
                        ('TrapFrequencies','axial_frequency'),
                        ('TrapFrequencies','radial_frequency_1'),
                        ('TrapFrequencies','radial_frequency_2'),
                        ('TrapFrequencies','rf_drive_frequency'),                       
                        ]
    rabi_required_parameters = [
                           ('RabiFlopping','rabi_amplitude_729'),
                           ('RabiFlopping','manual_scan'),
                           ('RabiFlopping','manual_frequency_729'),
                           ('RabiFlopping','line_selection'),
                           ('RabiFlopping','rabi_amplitude_729'),
                           ('RabiFlopping','frequency_selection'),
                           ('RabiFlopping','sideband_selection'),
                           
                           ('Crystallization', 'auto_crystallization'),
                           ('Crystallization', 'camera_record_exposure'),
                           ('Crystallization', 'camera_threshold'),
                           ('Crystallization', 'max_attempts'),
                           ('Crystallization', 'max_duration'),
                           ('Crystallization', 'min_duration'),
                           ('Crystallization', 'pmt_record_duration'),
                           ('Crystallization', 'pmt_threshold'),
                           ('Crystallization', 'use_camera'),

                           ('CalibrationScans', 'heating_rate_scan_interval'),
                           ]
    
    @classmethod
    def all_required_parameters(cls):
        parameters = set(cls.rabi_required_parameters)
        parameters = parameters.union(set(cls.trap_frequencies))
        parameters = parameters.union(set(excitation_729.all_required_parameters()))
        parameters = list(parameters)
        #removing parameters we'll be overwriting, and they do not need to be loaded
        parameters.remove(('Excitation_729','rabi_excitation_amplitude'))
        parameters.remove(('Excitation_729','rabi_excitation_duration'))
        parameters.remove(('Excitation_729','rabi_excitation_frequency'))
        return parameters
    
    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.rabi_flopping = self.make_experiment(rabi_flopping)
        self.rabi_flopping.initialize(cxn, context, ident)


        

    def run(self, cxn, context):	
        scan_param = self.parameters.CalibrationScans.heating_rate_scan_interval
        self.scan = scan_methods.simple_scan(scan_param, 'us')
	
	##parameters needed for fitting
	trap_freq = self.parameters.TrapFrequencies.axial_frequency *1e6 #in Hz	
	nbar = 10 #guess for nbar
	excitation_scaling=1.0 #change this if OP not working
	plot_flops=True #set to true to plot the flops
	theta=11.5 #the0 angle of the laser with the trap axis
	time_2pi=40 #guess for 2pi time in microseconds
	etas = [fitter.calc_eta(trap_freq,theta)]
	print etas
	delta={}
	
        for i,heat_time in enumerate(self.scan):
            replace = TreeDict.fromdict({
                                    'Heating.background_heating_time':heat_time,
                                       })
            self.rabi_flopping.set_parameters(replace)
            self.rabi_flopping.run(cxn, context)
	    self.rabi_flopping.finalize(cxn, context)
    

     
    #def finalize(self, cxn, context):
        


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = rabi_flopping_scan_heatingtime(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
