from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from subsequences.RepumpDwithDoppler import doppler_cooling_after_repump_d
from subsequences.EmptySequence import empty_sequence
from subsequences.OpticalPumping import optical_pumping
from subsequences.RabiExcitation import rabi_excitation
from subsequences.Tomography import tomography_readout
from subsequences.TurnOffAll import turn_off_all
from subsequences.SidebandCooling import sideband_cooling
from labrad.units import WithUnit
from treedict import TreeDict
from subsequences.advanceDACs import advanceDACs
from subsequences.resetDACs import resetDACs
from subsequences.forward_rampU2 import forward_ramp_U2
from subsequences.back_rampU2 import back_ramp_U2
import labrad
import time

class fast_change_dacs(pulse_sequence):
    
    required_parameters =  [
                            ('Heating', 'background_heating_time'),
                            ('OpticalPumping','optical_pumping_enable'), 
                            ('SidebandCooling','sideband_cooling_enable'),
                            
                            ('RepumpD_5_2','repump_d_duration'),
                            ('RepumpD_5_2','repump_d_frequency_854'),
                            ('RepumpD_5_2','repump_d_amplitude_854'),
                            
                            ('DACcontrol','U2target'),
                            ('DACcontrol','enable_ramp'),
                            ('DACcontrol','num_steps'),
                            ('DACcontrol','time_down'),
                            ('DACcontrol','time_up'),
                            ('DACcontrol','dac_pulse_length'),
                            
                            ('DopplerCooling', 'doppler_cooling_frequency_397'),
                            ('DopplerCooling', 'doppler_cooling_amplitude_397'),
                            ('DopplerCooling', 'doppler_cooling_frequency_866'),
                            ('DopplerCooling', 'doppler_cooling_amplitude_866'),
                            ('DopplerCooling', 'doppler_cooling_repump_additional'),
                            ('DopplerCooling', 'doppler_cooling_duration'),
                            
                            ('OpticalPumping','optical_pumping_frequency_729'),
                            ('OpticalPumping','optical_pumping_frequency_854'),
                            ('OpticalPumping','optical_pumping_frequency_866'),
                            ('OpticalPumping','optical_pumping_amplitude_729'),
                            ('OpticalPumping','optical_pumping_amplitude_854'),
                            ('OpticalPumping','optical_pumping_amplitude_866'),
                            ('OpticalPumping','optical_pumping_type'),
                            
                            ('OpticalPumpingContinuous','optical_pumping_continuous_duration'),
                            ('OpticalPumpingContinuous','optical_pumping_continuous_repump_additional'),
                          
                            ('OpticalPumpingPulsed','optical_pumping_pulsed_cycles'),
                            ('OpticalPumpingPulsed','optical_pumping_pulsed_duration_729'),
                            ('OpticalPumpingPulsed','optical_pumping_pulsed_duration_repumps'),
                            ('OpticalPumpingPulsed','optical_pumping_pulsed_duration_additional_866'),
                            ('OpticalPumpingPulsed','optical_pumping_pulsed_duration_between_pulses'),
                            
                            ('SidebandCooling','sideband_cooling_cycles'),
                            ('SidebandCooling','sideband_cooling_type'),
                            ('SidebandCooling','sideband_cooling_duration_729_increment_per_cycle'),
                            ('SidebandCooling','sideband_cooling_frequency_854'),
                            ('SidebandCooling','sideband_cooling_amplitude_854'),
                            ('SidebandCooling','sideband_cooling_frequency_866'),
                            ('SidebandCooling','sideband_cooling_amplitude_866'),
                            ('SidebandCooling','sideband_cooling_frequency_729'),
                            ('SidebandCooling','sideband_cooling_amplitude_729'),
                            ('SidebandCooling','sideband_cooling_optical_pumping_duration'),
                            
                            ('SidebandCoolingContinuous','sideband_cooling_continuous_duration'),
                          
                            ('SidebandCoolingPulsed','sideband_cooling_pulsed_duration_729'),
                            ('SidebandCoolingPulsed','sideband_cooling_pulsed_cycles'),
                            ('SidebandCoolingPulsed','sideband_cooling_pulsed_duration_repumps'),
                            ('SidebandCoolingPulsed','sideband_cooling_pulsed_duration_additional_866'),
                            ('SidebandCoolingPulsed','sideband_cooling_pulsed_duration_between_pulses'),
                          
                            ('Excitation_729','rabi_excitation_frequency'),
                            ('Excitation_729','rabi_excitation_amplitude'),
                            ('Excitation_729','rabi_excitation_duration'),
                            ('Excitation_729','rabi_excitation_phase'),

                            ('StateReadout','state_readout_frequency_397'),
                            ('StateReadout','state_readout_amplitude_397'),
                            ('StateReadout','state_readout_frequency_866'),
                            ('StateReadout','state_readout_amplitude_866'),
                            ('StateReadout','state_readout_duration'),
                            ('StateReadout','use_camera_for_readout'),
                            
                            ('Tomography', 'rabi_pi_time'),
                            ('Tomography', 'iteration'),
                            ('Tomography', 'tomography_excitation_frequency'),
                            ('Tomography', 'tomography_excitation_amplitude'),
                            ]
    
    
    required_subsequences = [turn_off_all, advanceDACs, 
                             resetDACs]

    def sequence(self):
        p = self.parameters
        #electrode_dict = ['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21']
        tot_time = p.DACcontrol.time_up
        time_at_top = tot_time-12
        
        
    
       
        electrode_dict = ['06']
        i = 0
        cxn = labrad.connect()
        current_multipoles =cxn.dac_server.get_multipole_values()
        currentU2 = dict(current_multipoles)['U2']
        targetU2 = p.DACcontrol.U2target
        amplitude = (targetU2 - currentU2)
        #readfromfile =True;
        #filter1ms = True;
        readfromfile = True;
        v = []
        f= ''
        print 'C:\Users\expcontrol\Downloads\\' +str(int(time_at_top)) +'msec_at_top.txt'
        if(readfromfile):
            z= 'C:\Users\expcontrol\Downloads\\' +str(int(time_at_top)) +'msec_at_top.txt'
            print z
            f = open(z,'r')
                
        for line in f:
            #print line
            try:
                temp= float(line)
              
                v.append(temp*amplitude+currentU2)
            except ValueError:
                print 'error'
        
        import time 
        from time import sleep
        print f
        #v = range(126)
        time.sleep(2)
            
        if(readfromfile):
            print 'yp'
            while i < p.DACcontrol.num_steps:
                cxn.dac_server.set_next_u2(v[i])
                i= i+1  
            cxn.dac_server.set_next_u2(currentU2)
        else:     
            while i <1:
                for elect in electrode_dict:
                    cxn.dac_server.set_voltage([(elect,0)])
                i= i+1
            while i <p.DACcontrol.num_steps/2.0:
                for elect in electrode_dict:
                    cxn.dac_server.set_voltage([(elect,2)])
                i=i+1
            while i <p.DACcontrol.num_steps-1:
                for elect in electrode_dict:
                    cxn.dac_server.set_voltage([(elect,4)])
                i=i+1
            print i
            for elect in electrode_dict:
                cxn.dac_server.set_voltage([(elect,0)])
        
        print cxn.dac_server.get_analog_voltages()
        print 'Setting U2 to:', p.DACcontrol.U2target
        self.end = WithUnit(10, 'us')
        #self.addSequence(turn_off_all)
        #self.addSequence(doppler_cooling_after_repump_d)
        #if p.OpticalPumping.optical_pumping_enable:
        #    self.addSequence(optical_pumping)
        #if p.SidebandCooling.sideband_cooling_enable:
        #    self.addSequence(sideband_cooling)
        
        # ramp down if toggled
        if(p.DACcontrol.enable_ramp):
            print 'enabled'
            self.addSequence(advanceDACs)#forward_ramp_U2
        print 'finished advance' 
        
        print cxn.dac_server.get_analog_voltages()
#        print cxn.dac_server.get_analog_voltages()
        if(p.DACcontrol.enable_ramp):
            print 'enabled'
            cxn.dac_server.reset_queue()
            self.addSequence(resetDACs)
        print 'end'
        f.close()
        #self.addSequence(empty_sequence, TreeDict.fromdict({'EmptySequence.empty_sequence_duration':p.Heating.background_heating_time}))
        
        
        #if(p.DACcontrol.enable_ramp):
        #    self.addSequence(back_ramp_U2)
        #self.addSequence(rabi_excitation)
        #self.addSequence(tomography_readout)
        

def step(x):
    if(x>= 0):
        return 1
    else:
        return 0

def step2(x):
    if(x> 0):
        return 1
    else:
        return 0
