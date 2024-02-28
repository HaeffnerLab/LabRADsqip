class config(object):

    #list in the format (import_path, class_name)
    sequences = [

        #('sqip.Pulsesequence2.RabiFloppingManual', 'RabiFloppingManual'),
        ('sqip.Pulsesequence2.Spectrum', 'Spectrum'),
        ('sqip.Pulsesequence2.RabiFlopping', 'RabiFlopping'),
        #('sqip.Pulsesequence2.Ramsey', 'Ramsey'),
        ('sqip.Pulsesequence2.CalibAllLines', 'CalibAllLines'),
        #('sqip.Pulsesequence2.test', 'test'),
        ('sqip.Pulsesequence2.DriftTrackerRamsey', 'DriftTrackerRamsey'),
        # ('sqip.Pulsesequence2.DriftTrackerRamsey_auto_schedule', 'DriftTrackerRamsey_auto_schedule'),
        #('sqip.Pulsesequence2.CalibAllLines_global', 'CalibAllLines_global'),
        #('sqip.Pulsesequence2.DriftTrackerRamsey_global', 'DriftTrackerRamsey_global'),
        #('sqip.Pulsesequence2.Heating_Rate', 'Heating_Rate'),
        ('sqip.Pulsesequence2.Heating_Rate_Rabi', 'Heating_Rate_Rabi'),
        #('sqip.Pulsesequence2.Heating_Rate_BlueRabi', 'Heating_Rate_BlueRabi'),
        ('sqip.Pulsesequence2.ScanMicromotion', 'ScanMicromotion'),
        ('sqip.Pulsesequence2.OptimizeDopplerCooling', 'Calibrations_DopplerCooling')
        
        
        
        ]
    
    global_show_params= [
                        # 'ScanParam.shuffle',
                         'global_scan_options.quick_finish',
                         'DriftTracker.global_sd_enable',
                         'DopplerCooling.doppler_cooling_amplitude_397',
                         'DopplerCooling.doppler_cooling_frequency_397',
                         'DopplerCooling.doppler_cooling_duration',
                         'DopplerCooling.doppler_cooling_repump_additional',
                         'DopplerCooling.doppler_cooling_amplitude_866',
                         'DopplerCooling.doppler_cooling_frequency_866',
                         # 'DopplerCooling.pre_duration',
                         
                         'Excitation_729.channel_729',
                         # 'Excitation_729.bichro',
                         
                         'OpticalPumping.line_selection',
                         'OpticalPumping.optical_pumping_type',
                         'OpticalPumping.optical_pumping_amplitude_729',
                         'OpticalPumping.optical_pumping_amplitude_866',
                         'OpticalPumping.optical_pumping_amplitude_854',
                         'OpticalPumping.optical_pumping_frequency_854',
                         'OpticalPumping.optical_pumping_frequency_866',
                         # 'OpticalPumpingAux.aux_op_line_selection',
                         
                         'Heating.background_heating_time',
                         
                         # 'SidebandCooling.selection_sideband',
                         # 'SidebandCooling.order',
                         # 'SidebandCooling.line_selection',
                         # 'SidebandCooling.sideband_cooling_amplitude_854',
                         
                         # 'SequentialSBCooling.channel_729',
                         # 'SequentialSBCooling.selection_sideband',                       
                         # 'SequentialSBCooling.order',
                         # 'SequentialSBCooling.enable',
                         
                         
                         'StatePreparation.channel_729',
                         # 'StatePreparation.aux_optical_pumping_enable',
                         'StatePreparation.optical_pumping_enable',
                         'StatePreparation.sideband_cooling_enable',

                         'StateReadout.readout_mode',
                         'StateReadout.state_readout_amplitude_397',
                         'StateReadout.state_readout_frequency_397',
                         'StateReadout.state_readout_amplitude_866',
                         'StateReadout.state_readout_frequency_866',
                         'StateReadout.state_readout_duration',
                         'StateReadout.threshold_list',
                         'TrapFrequencies.axial_frequency',
                         'TrapFrequencies.radial_frequency_1',
                         'TrapFrequencies.radial_frequency_2',
                         'TrapFrequencies.rf_drive_frequency',
                         #'StateReadout.use_camera_for_readout',
                         
                      
                                                  
                       ]


    allowed_concurrent = {
#        'fft_spectrum': ['non_conflicting_experiment'],
#        'non_conflicting_experiment' : ['fft_spectrum'],
    }
    
    launch_history = 1000              

    quick_finish_path = "/home/sqip/Data/"
