class config(object):

    #list in the format (import_path, class_name)
##    scripts = [
##         #      ('sqip.scripts.experiments.cavityscan.scan_cavity_397','scan_cavity_397'), 
##               ('sqip.scripts.experiments.FFT.fft_spectrum','fft_spectrum'),
##               ('sqip.scripts.experiments.Experiments729.rabi_flopping','rabi_flopping'),
##               ('sqip.scripts.experiments.Experiments729.spectrum','spectrum'),
##               ('sqip.scripts.experiments.Experiments729.drift_tracker_ramsey','drift_tracker_ramsey'),
##               ('sqip.scripts.experiments.VoltageRamping.ramp_multipole','ramp_multipole'),
##               ('sqip.scripts.experiments.VoltageRamping.adiabatic_cooling_test','adiabatic_cooling_test'),
##               ('sqip.scripts.experiments.VoltageRamping.ramped_delocalization','ramped_delocalization'),
##               ('sqip.scripts.experiments.Experiments729.rabi_flop_scannable', 'rabi_flopping_scannable')
##                              
##               ]

    scripts = [
         #      ('sqip.scripts.experiments.cavityscan.scan_cavity_397','scan_cavity_397'),
               ('sqip.scripts.experiments.CalibrationScans.calibrate_all_lines','calibrate_all_lines'),
		('sqip.scripts.experiments.CalibrationScans.scan_micromotion','scan_micromotion'),
               ('sqip.scripts.experiments.CalibrationScans.calibrate_temperature','calibrate_temperature'),
               ('sqip.scripts.experiments.CalibrationScans.calibrate_heating_rates','calibrate_heating_rates'),
		('sqip.scripts.experiments.CalibrationScans.rabi_flopping_scan_heatingtime','rabi_flopping_scan_heatingtime'),
		('sqip.scripts.experiments.CalibrationScans.rabi_flopping_scan_heatingtime_test1','rabi_flopping_scan_heatingtime_test1'),
               ('sqip.scripts.experiments.CalibrationScans.rabi_calib_heating_rate','rabi_calib_heating_rate'),
               ('sqip.scripts.experiments.FFT.fft_spectrum','fft_spectrum'),
               ('sqip.scripts.experiments.Experiments729.rabi_flopping','rabi_flopping'),
		('sqip.scripts.experiments.Experiments729.rabi_flopping_with_ramping','rabi_flopping_with_ramping'),
               ('sqip.scripts.experiments.Experiments729.spectrum','spectrum'),
              # ('sqip.scripts.experiments.Experiments729.drift_tracker_ramsey','drift_tracker_ramsey'),
               #('sqip.scripts.experiments.VoltageRamping.ramp_multipole','ramp_multipole'),

               #('sqip.scripts.experiments.VoltageRamping.ramped_delocalization','ramped_delocalization'),
               ('sqip.scripts.experiments.Experiments729.rabi_flop_scannable', 'rabi_flopping_scannable'),
               ('sqip.scripts.experiments.Experiments729.spectrum_with_ramping', 'spectrum_with_ramping'),
        ('sqip.scripts.experiments.Experiments729.ramsey_scangap','ramsey_scangap')

                              
               ]

#    allowed_concurrent = {
#        'fft_spectrum': ['non_conflicting_experiment'],
#        'non_conflicting_experiment' : ['fft_spectrum'],
#    }
    
    launch_history = 1000               

