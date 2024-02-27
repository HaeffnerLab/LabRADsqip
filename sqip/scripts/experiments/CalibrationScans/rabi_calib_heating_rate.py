from sqip.scripts.experiments.Experiments729.rabi_flopping import rabi_flopping
from sqip.scripts.experiments.CalibrationScans.calibrate_all_lines import calibrate_all_lines
from common.abstractdevices.script_scanner.scan_methods import experiment
from sqip.scripts.experiments.Experiments729.excitations import excitation_729
from sqip.scripts.scriptLibrary.common_methods_729 import common_methods_729 as cm
from common.abstractdevices.script_scanner.scan_methods import experiment
from sqip.scripts.experiments.CalibrationScans.calibrate_temperature import calibrate_temperature
from sqip.scripts.scriptLibrary import scan_methods
from sqip.scripts.scriptLibrary import dvParameters
from fitters import peak_fitter
from labrad.units import WithUnit
from treedict import TreeDict
import time
import numpy as np
import labrad
from fitters import rate_from_flops_fitter
import math
import datetime
import os

class rabi_calib_heating_rate(experiment):

    name = 'RabiCalibHeatingRates'

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
        #self.drift_tracker = cxn.sd_tracker
        #self.calibrate_temp = self.make_experiment(calibrate_temperature)
        #self.calibrate_temp.initialize(cxn, context, ident)

        self.rabi_flopping = self.make_experiment(rabi_flopping)
        self.rabi_flopping.initialize(cxn, context, ident)
        self.fitter = rate_from_flops_fitter()

        #this section is to add line calibrations
        self.calib_all_lines = self.make_experiment(calibrate_all_lines)
        self.calib_all_lines.initialize(cxn, context, ident)
        

        self.save_context = cxn.context()
        self.dv = cxn.data_vault
        self.pv = cxn.parametervault
        #self.dds_cw = cxn.dds_cw
        self.cxnlab = labrad.connect('192.168.169.49', password='lab', tls_mode='off') #connection to labwide network
        
    def run(self, cxn, context):

        dv_args = {'output_size': 2,
                    'experiment_name' : self.name,
                    'window_name': 'heatingrate',
                    'dataset_name' : 'Heating_Rate'
                    }

        scan_methods.setup_data_vault(cxn, self.save_context, dv_args)

        scan_param = self.parameters.CalibrationScans.heating_rate_scan_interval

        self.scan = scan_methods.simple_scan(scan_param, 'us')

        nbarlist=[]
        nbarerrlist=[]
        heattimes=[]
        for i,heat_time in enumerate(self.scan):
            #should_stop = self.pause_or_stop()
            #if should_stop: break
            
            #####
            #figure out how to put a caliballlines in here with 0 heating time
            #replace = TreeDict.fromdict({
             #                       'Heating.background_heating_time':WithUnit(0.0, 'ms')
              #                         })
            #self.calib_all_lines.set_parameters(replace)
            #self.calib_all_lines.run(cxn, context)


            ####
            
            replace = TreeDict.fromdict({
                                    'Heating.background_heating_time':heat_time,
                                    'Documentation.sequence':'calibrate_heating_rates',
                                       })
            self.rabi_flopping.set_parameters(replace)
            

            t,ex = self.rabi_flopping.run(cxn, context)
            t = np.array(t)
            ex = np.array(ex)
            ex = ex.flatten()
            trap_freq = self.parameters.TrapFrequencies.axial_frequency['Hz']
            
            
            if heat_time == 0:
                time_2pi = self.fitter.calc_2pitime(t,ex)
                excitation_scaling = 0.99
                nbar,nbarerr,time_2pi,excitation_scaling = self.fitter.fit_single_flop(heat_time,t,ex,trap_freq,time_2pi,excitation_scaling)
            else:
                nbar,nbarerr,temp,temp1 = self.fitter.fit_single_flop(heat_time,t,ex,trap_freq,time_2pi,excitation_scaling)

            
            #submission is for the data vault for grapher. not sure how to add the error in

            
            submission = [heat_time['ms']]
            submission.extend([nbar,nbarerr])
    
            if not math.isnan(nbarerr):
                self.dv.add(submission, context = self.save_context)
                heattimes.append(heat_time['ms'])
                nbarlist.append(nbar)
                nbarerrlist.append(nbarerr)
            
            self.rabi_flopping.finalize(cxn, context)
        print 'here are the results'
        print nbarlist
        print nbarerrlist
        rate, stderr = self.fitter.fit_heating_rate(heattimes, nbarlist, nbarerrlist)

        try:
            f = open('/home/sqip/HeatingRateData/rates' + datetime.date.today().strftime('%d_%m_%y')+'.txt','a')
        except IOError:
            print 'creating new file'
            f = open('/home/sqip/HeatingRateData/rates' + datetime.date.today().strftime('%d_%m_%y')+'.txt','w')
            

        f.write("%.2f" % rate + ',' + "%.2f" % stderr + ',' + datetime.datetime.now().strftime("%X")+"\n")
        print f
        f.close()
            
            
    def finalize(self, cxn, context):
        self.rabi_flopping.save_parameters(self.dv, cxn, self.cxnlab, self.save_context)

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = rabi_calib_heating_rate(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
