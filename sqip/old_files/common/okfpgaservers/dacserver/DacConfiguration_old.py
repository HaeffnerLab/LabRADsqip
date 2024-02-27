# Configuration file for the dac

class channelConfiguration(object):
    """
Stores complete information for each DAC channel
"""
    def __init__(self, dacChannelNumber, trapElectrodeNumber = None, smaOutNumber = None, name = None, boardVoltageRange = (-10, 10), allowedVoltageRange = (-8, 8)):
        self.dacChannelNumber = dacChannelNumber
        self.trapElectrodeNumber = trapElectrodeNumber
        self.smaOutNumber = smaOutNumber
        self.boardVoltageRange = boardVoltageRange
        self.allowedVoltageRange = allowedVoltageRange
        if (name == None) & (trapElectrodeNumber != None):
            self.name = str(trapElectrodeNumber)
            if trapElectrodeNumber < 10: self.name +=' '
        else:
            self.name = name

class hardwareConfiguration(object):
    numElectrodes = 9
    numSmaOuts = 5
    numDacChannels = 28
    PREC_BITS = 16
    centerElectrode = 9
    EXPNAME = 'SQIP'
    pulseTriggered = False
    multipoles = ['Ex1', 'Ey1', 'Ez1', 'U2']
#    multipoles = ['Ex1', 'Ey1', 'Ez1','U1', 'U2', 'U3']
    maxCache = 126 # Max number of voltages which can be cached to the DAC
    
# elecDict assign software channel 'N' to DAC number 'M', example:
#'N ': channelConfiguration(M, trapElectrodeNumber = N),
    elecDict = {        
        '1 ': channelConfiguration(2+5, trapElectrodeNumber = 1),
        '2 ': channelConfiguration(3+5, trapElectrodeNumber = 2),
        '3 ': channelConfiguration(4+5, trapElectrodeNumber = 3),
        '4 ': channelConfiguration(5+5, trapElectrodeNumber = 4),
        '5 ': channelConfiguration(17+5, trapElectrodeNumber = 5),
        '6 ': channelConfiguration(10+5, trapElectrodeNumber = 6),
        '7 ': channelConfiguration(11+5, trapElectrodeNumber = 7),
        '8 ': channelConfiguration(12+5, trapElectrodeNumber = 8),
        '9 ': channelConfiguration(16+5, trapElectrodeNumber = 9),
#        '10': channelConfiguration(16+5, trapElectrodeNumber = 10)

#        '1 ': channelConfiguration(1+5, trapElectrodeNumber = 1),
#        '2 ': channelConfiguration(2+5, trapElectrodeNumber = 2),
#        '3 ': channelConfiguration(3+5, trapElectrodeNumber = 3),
#        '4 ': channelConfiguration(4+5, trapElectrodeNumber = 4),
#        '5 ': channelConfiguration(5+5, trapElectrodeNumber = 5),
#        '6 ': channelConfiguration(6+5, trapElectrodeNumber = 6),
#        '7 ': channelConfiguration(7+5, trapElectrodeNumber = 7),
#        '8 ': channelConfiguration(8+5, trapElectrodeNumber = 8),
#        '9 ': channelConfiguration(9+5, trapElectrodeNumber = 9),
#        '10': channelConfiguration(10+5, trapElectrodeNumber = 10),
#        '11': channelConfiguration(11+5, trapElectrodeNumber = 11),
#        '12': channelConfiguration(12+5, trapElectrodeNumber = 12),
#        '13': channelConfiguration(13+5, trapElectrodeNumber = 13),
#        '14': channelConfiguration(14+5, trapElectrodeNumber = 14),
#        '15': channelConfiguration(16+5, trapElectrodeNumber = 15), ###
#        '16': channelConfiguration(23, trapElectrodeNumber = 16),        
#        '17': channelConfiguration(4, trapElectrodeNumber = 17),        
#        '18': channelConfiguration(19, trapElectrodeNumber = 18),
#        '19': channelConfiguration(17, trapElectrodeNumber = 19),
#        '20': channelConfiguration(21, trapElectrodeNumber = 20),
        #'21': channelConfiguration(20, trapElectrodeNumber = 21),
        #'22': channelConfiguration(12, trapElectrodeNumber = 22),
        #'23': channelConfiguration(10, trapElectrodeNumber = 23),
        }

    smaDict = {
        'RF bias': channelConfiguration(1, smaOutNumber = 1, name = 'RF bias', boardVoltageRange = (-10., 10.), allowedVoltageRange = (-10.0, 10.0)),
        # 'test': channelConfiguration(2, smaOutNumber = 2, name = 'test', boardVoltageRange = (-10., 10.), allowedVoltageRange = (-2.0, 0)),
        }