class channelConfiguration(object):
    """
    Stores complete information for each DAC channel
    """


    def __init__(self, dacChannelNumber, trapElectrodeNumber = None, smaOutNumber = None, name = None, boardVoltageRange = (-10, 10), allowedVoltageRange = (-35, 35)):
        self.dacChannelNumber = dacChannelNumber
        self.trapElectrodeNumber = trapElectrodeNumber
        self.smaOutNumber = smaOutNumber
        self.boardVoltageRange = boardVoltageRange
        self.allowedVoltageRange = allowedVoltageRange
        if (name == None) & (trapElectrodeNumber != None):
            self.name = str(trapElectrodeNumber).zfill(2)
        else:
            self.name = name
    
    def computeDigitalVoltage(self, analogVoltage):
        return int(round(sum([ self.calibration[n] * analogVoltage ** n for n in range(len(self.calibration)) ])))

class hardwareConfiguration(object):
    EXPNAME = 'SQIP'
    default_multipoles =  ['Ex', 'Ey', 'Ez', 'U1', 'U2', 'U3', 'U4', 'U5'] #['Ey', 'Ez', 'Ex', 'U3', 'U4', 'U2', 'U5', 'U1'] #['Ey', 'Ez', 'Ex', 'U1', 'U2', 'U3', 'U4', 'U5', 'U6', 'U7', 'U8', 'U9', 'U10','U11', 'U12', 'U13','U14','U15', 'U16', 'U17','U18','U19', 'U20', 'U21']# 

    okDeviceID = 'DAC Controller'
    okDeviceFile = 'control_noninverted.bit'
    #okDeviceID = 'dac5'
    #okDeviceFile = 'dac5.bit'
    
    
    centerElectrode = 21 #write False if no Centerelectrode
    PREC_BITS = 16
    pulseTriggered = False
    maxCache = 126
    filter_RC = 5e4 * 4e-7
# elecDict assign software channel 'N' to DAC number 'M', example:
#'N ': channelConfiguration(M, trapElectrodeNumber = N),

    elec_dict = {
        '01': channelConfiguration(2, trapElectrodeNumber=1),
        '02': channelConfiguration(3, trapElectrodeNumber=2),
        '03': channelConfiguration(26, trapElectrodeNumber=3),
        '04': channelConfiguration(21, trapElectrodeNumber=4),
        '05': channelConfiguration(12, trapElectrodeNumber=5),
        '06': channelConfiguration(23, trapElectrodeNumber=6),## ?!  
        '07': channelConfiguration(24, trapElectrodeNumber=7),
        '08': channelConfiguration(25, trapElectrodeNumber=8), 
        '09': channelConfiguration(22, trapElectrodeNumber=9), 
        '10': channelConfiguration(11, trapElectrodeNumber=10),   
                     
        '11': channelConfiguration(7, trapElectrodeNumber=11), 
        '12': channelConfiguration(6, trapElectrodeNumber=12),
        '13': channelConfiguration(14, trapElectrodeNumber=13),
        '14': channelConfiguration(15, trapElectrodeNumber=14),
        '15': channelConfiguration(16, trapElectrodeNumber=15),
        '16': channelConfiguration(17, trapElectrodeNumber=16),## ?!
        '17': channelConfiguration(8, trapElectrodeNumber=17),
        '18': channelConfiguration(9, trapElectrodeNumber=18),
        '19': channelConfiguration(18, trapElectrodeNumber=19),
        '20': channelConfiguration(19,  trapElectrodeNumber=20),
        
        '21': channelConfiguration(20, trapElectrodeNumber=21),## ?! rewired
        # re-route non-working chip 10 to 26 
        # Dsub 5 and 21 are switched
        # Dsub 4 and 10 are switched
        
        #'22': channelConfiguration(27, trapElectrodeNumber=22),
        #'23': channelConfiguration(28, trapElectrodeNumber=23), 
        #'24': channelConfiguration(1, trapElectrodeNumber=24),
        #'25': channelConfiguration(4, trapElectrodeNumber=25),
        #'26': channelConfiguration(15,  trapElectrodeNumber=26),
        #'27': channelConfiguration(20, trapElectrodeNumber=27),
        #'28': channelConfiguration(25, trapElectrodeNumber=28) 
        }

    notused_dict = {
               }

    sma_dict = {
        'RF bias': channelConfiguration(13, smaOutNumber=1, name='RF bias', boardVoltageRange=(-10., 10.), allowedVoltageRange=(-2.0, 0)),
      #  'Test FPGA 1':channelConfiguration(13, smaOutNumber=2, name='Test FPGA 1', boardVoltageRange=(-10., 10.), allowedVoltageRange=(-10.0, 10)),
        'Test FPGA 2':channelConfiguration(30, smaOutNumber=3, name='Test FPGA 2', boardVoltageRange=(-10., 10.), allowedVoltageRange=(-10.0, 10))  # broken channel?
        }

'''

===== Chip-electrode |||  CLCC number  |||  D-Sub number =====

        E1           |||               |||    5
        E2           |||               |||    17
        E3           |||               |||    16
        E4           |||               |||    15
        E5           |||               |||    11
        E6           |||               |||    10
        E7           |||               |||    23
        E8           |||               |||    24
        E9           |||               |||    25
        E10          |||               |||    22
        E11          |||               |||    3
        E12          |||               |||    2
        E13          |||               |||    14
        E14          |||               |||    6
        E15          |||               |||    7
        E16          |||               |||    20
        E17          |||               |||    19
        E18          |||               |||    18
        E19          |||               |||    21
        E20          |||               |||    9
        E21 (CNT)    |||               |||    8
              


    elec_dict = {
        '01': channelConfiguration(2, trapElectrodeNumber=1),
        '02': channelConfiguration(3, trapElectrodeNumber=2),
        '03': channelConfiguration(4, trapElectrodeNumber=3),
        '04': channelConfiguration(5, trapElectrodeNumber=4),
        '05': channelConfiguration(13, trapElectrodeNumber=5),
        '06': channelConfiguration(12, trapElectrodeNumber=6),## ?!  
        '07': channelConfiguration(23, trapElectrodeNumber=7),
        '08': channelConfiguration(24, trapElectrodeNumber=8), 
        '09': channelConfiguration(22, trapElectrodeNumber=9),
        '10': channelConfiguration(11, trapElectrodeNumber=10),   
                     
        '11': channelConfiguration(7, trapElectrodeNumber=11), 
        '12': channelConfiguration(6, trapElectrodeNumber=12),
        '13': channelConfiguration(15, trapElectrodeNumber=13),
        '14': channelConfiguration(16, trapElectrodeNumber=14),
        '15': channelConfiguration(17, trapElectrodeNumber=15),
        '16': channelConfiguration(8, trapElectrodeNumber=16),## ?!
        '17': channelConfiguration(21, trapElectrodeNumber=17),
        '18': channelConfiguration(9, trapElectrodeNumber=18),
        '19': channelConfiguration(18, trapElectrodeNumber=19),
        '20': channelConfiguration(19,  trapElectrodeNumber=20),
        
        '21': channelConfiguration(10, trapElectrodeNumber=21),## ?!
        #'22': channelConfiguration(27, trapElectrodeNumber=22),
        #'23': channelConfiguration(28, trapElectrodeNumber=23), 
        #'24': channelConfiguration(1, trapElectrodeNumber=24),
        #'25': channelConfiguration(4, trapElectrodeNumber=25),
        #'26': channelConfiguration(15,  trapElectrodeNumber=26),
        #'27': channelConfiguration(20, trapElectrodeNumber=27),
        #'28': channelConfiguration(25, trapElectrodeNumber=28) 
        }




        '01': channelConfiguration(5, trapElectrodeNumber=1),
        '02': channelConfiguration(17, trapElectrodeNumber=2),
        '03': channelConfiguration(16, trapElectrodeNumber=3),
        '04': channelConfiguration(15, trapElectrodeNumber=4),
        '05': channelConfiguration(11, trapElectrodeNumber=5),
        '06': channelConfiguration(26, trapElectrodeNumber=6),## ?!  chip 28 connected to pin 10 ( E6 -> DSUB 10 )
        '07': channelConfiguration(23, trapElectrodeNumber=7),
        '08': channelConfiguration(24, trapElectrodeNumber=8), 
        '09': channelConfiguration(25, trapElectrodeNumber=9),
        '10': channelConfiguration(22, trapElectrodeNumber=10),                
        '11': channelConfiguration(3, trapElectrodeNumber=11), 
        '12': channelConfiguration(2, trapElectrodeNumber=12),
        '13': channelConfiguration(14, trapElectrodeNumber=13),
        '14': channelConfiguration(6, trapElectrodeNumber=14),
        '15': channelConfiguration(7, trapElectrodeNumber=15),
        '16': channelConfiguration(10, trapElectrodeNumber=16),## ?!  this is pin 20 due to rewiring
        '17': channelConfiguration(19, trapElectrodeNumber=17),
        '18': channelConfiguration(18, trapElectrodeNumber=18),
        '19': channelConfiguration(21, trapElectrodeNumber=19),
        '20': channelConfiguration(9,  trapElectrodeNumber=20),
        '21': channelConfiguration(8, trapElectrodeNumber=21),
                     
                     
'''
    
