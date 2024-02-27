from common.devel.bum.sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U
from treedict import TreeDict

####Needs major editing ####


class StatePreparation(pulse_sequence):
    
    #name = 'State preparation'

    scannable_params = {
                        }

    show_params= ['DopplerCooling.doppler_cooling_duration', 'OpticalPumping.optical_pumping_enable','SidebandCooling.sideband_cooling_enable'

                  ]

    def sequence(self):
        print "STARTING STATE PREP"
        print self.start
        
        from subsequences.TurnOffAll import TurnOffAll
        from subsequences.RepumpD import RepumpD
        from subsequences.DopplerCooling import DopplerCooling
        from subsequences.OpticalPumping import OpticalPumping
        from subsequences.SidebandCooling import SidebandCooling
        from subsequences.EmptySequence import EmptySequence
        
        self.end = U(10., 'us')
        self.addSequence(TurnOffAll)
        self.addSequence(RepumpD) # initializing the state of the ion
        self.addSequence(DopplerCooling) 
        
        if self.parameters.StatePreparation.optical_pumping_enable:
            self.addSequence(OpticalPumping)
            
  
        # side band cooling             
        if self.parameters.StatePreparation.sideband_cooling_enable:
            sc = self.parameters.SidebandCooling       
            duration_op= sc.sideband_cooling_optical_pumping_duration
            for i in range(int(self.parameters.SidebandCooling.sideband_cooling_cycles)):
                print "sideband cooling"
                self.addSequence(SidebandCooling)
                self.addSequence(OpticalPumping, {"OpticalPumpingContinuous.optical_pumping_continuous_duration":duration_op,
                                                  "OpticalPumping.optical_pumping_type" : 'continuous',
                                                 }) # apply an additional full optical pumping aftereach cycle
                
                if self.parameters.SequentialSBCooling.enable:
                    print "sequential side band cooling"
                    sbc=self.parameters.SequentialSBCooling
                    # replacing the channel, sideband and order 
                    self.addSequence(SidebandCooling,{"StatePreparation.channel_729" : sbc.channel_729,
                                                      # "SidebandCooling.selection_sideband" : sbc.selection_sideband,
                                                      # "SidebandCooling.order" : sbc.order
                                                      # use old sideband parameter to replace
                                                      "SidebandCooling.sideband_selection" : sbc.sideband_selection,
                                                      })
                    self.addSequence(OpticalPumping, {"OpticalPumpingContinuous.optical_pumping_continuous_duration":duration_op,
                                                      "OpticalPumping.optical_pumping_type" : 'continuous',
                                                     })

        # if self.parameters.StatePreparation.optical_pumping_enable:
        #     self.addSequence(OpticalPumping)
            
          
        self.addSequence(EmptySequence,  { "EmptySequence.empty_sequence_duration" : self.parameters.Heating.background_heating_time})