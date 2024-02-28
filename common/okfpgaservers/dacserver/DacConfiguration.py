class channelConfiguration(object):
    """
    Stores complete information for each DAC channel
    """

    def __init__(self, dacChannelNumber, trapElectrodeNumber = None, smaOutNumber = None, name = None, 
        boardVoltageRange = (-30, 30), allowedVoltageRange = (-30, 30), scale = 1):
        self.dacChannelNumber = dacChannelNumber
        self.trapElectrodeNumber = trapElectrodeNumber
        self.smaOutNumber = smaOutNumber
        self.boardVoltageRange = boardVoltageRange
        self.allowedVoltageRange = allowedVoltageRange
        self.scale = scale
        if (name == None) & (trapElectrodeNumber != None):
            self.name = str(trapElectrodeNumber).zfill(2)
        else:
            self.name = name

    def computeDigitalVoltage(self, analogVoltage):
        return int(round(sum([ self.calibration[n] * (analogVoltage / self.scale) ** n for n in range(len(self.calibration)) ])))

class hardwareConfiguration(object):
    EXPNAME = 'SQIP'
    default_multipoles = ['Ex', 'Ey', 'Ez', 'U1','U2','U3','U4','U5']
    okDeviceID = 'Pulser2'
    okDeviceFile = 'dac.bit'
    centerElectrode = 21 #write False if no Centerelectrode
    PREC_BITS = 16
    pulseTriggered = True
    maxCache = 1000
    filter_RC = 5e4 * 4e-7
    elec_dict = {
        '01': channelConfiguration(2, trapElectrodeNumber=1),
        '02': channelConfiguration(3, trapElectrodeNumber=2),
        '03': channelConfiguration(4, trapElectrodeNumber=3),
        '04': channelConfiguration(5, trapElectrodeNumber=4),
        '05': channelConfiguration(9, trapElectrodeNumber=5),
        '06': channelConfiguration(21, trapElectrodeNumber=6),
        '07': channelConfiguration(18, trapElectrodeNumber=7,scale=1.301),
        '08': channelConfiguration(19, trapElectrodeNumber=8),
        '09': channelConfiguration(6, trapElectrodeNumber=9),
        '10': channelConfiguration(8, trapElectrodeNumber=10), # broken, ground outside
        '11': channelConfiguration(10, trapElectrodeNumber=11), # broken, ground outside
        '12': channelConfiguration(22, trapElectrodeNumber=12),
        '13': channelConfiguration(15, trapElectrodeNumber=13),
        '14': channelConfiguration(16, trapElectrodeNumber=14),
        '15': channelConfiguration(17, trapElectrodeNumber=15),
        '16': channelConfiguration(11, trapElectrodeNumber=16,scale=1.3445),
        '17': channelConfiguration(12, trapElectrodeNumber=17),
        '18': channelConfiguration(13, trapElectrodeNumber=18),
        '19': channelConfiguration(23, trapElectrodeNumber=19),
        '20': channelConfiguration(24, trapElectrodeNumber=20),
        '21': channelConfiguration(25, trapElectrodeNumber=21),
        }

    notused_dict = {
        #'28': channelConfiguration(22, trapElectrodeNumber=28)
               }

    sma_dict = {
        'RF bias': channelConfiguration(26, smaOutNumber=1, name='RF bias', boardVoltageRange=(-10., 10.), allowedVoltageRange=(-2.0, 0)),
        #'DSub13': channelConfiguration(13, smaOutNumber=2, name='DSub13', boardVoltageRange=(-10., 10.), allowedVoltageRange=(0.0, 0.0)),
        #'DSub10': channelConfiguration(10, smaOutNumber=1, name='DSub13', boardVoltageRange=(-10., 10.), allowedVoltageRange=(1.0, 0.0)),
        }
        # '01': channelConfiguration(15, trapElectrodeNumber=1),
        # '02': channelConfiguration(16, trapElectrodeNumber=2, scale=0.995),
        # '03': channelConfiguration(17, trapElectrodeNumber=3, scale=0.961),
        # '04': channelConfiguration(11, trapElectrodeNumber=4, scale=0.938),
        # '05': channelConfiguration(12, trapElectrodeNumber=5, scale=1.14),
        # '06': channelConfiguration(13, trapElectrodeNumber=6, scale= 0.834),
        # '07': channelConfiguration(23, trapElectrodeNumber=7, scale = 1.183),
        # '08': channelConfiguration(24, trapElectrodeNumber=8, scale = 0.927),
        # '09': channelConfiguration(22, trapElectrodeNumber=9, scale = 0.948),
        # '10': channelConfiguration(25, trapElectrodeNumber=10, scale = 0.959), # broken, ground outside
        # '11': channelConfiguration(20, trapElectrodeNumber=11), # broken, ground outside
        # '12': channelConfiguration(2, trapElectrodeNumber=12),
        # '13': channelConfiguration(3, trapElectrodeNumber=13),
        # '14': channelConfiguration(4, trapElectrodeNumber=14),
        # '15': channelConfiguration(5, trapElectrodeNumber=15),
        # '16': channelConfiguration(9, trapElectrodeNumber=16,scale=1.301),
        # '17': channelConfiguration(21, trapElectrodeNumber=17),
        # '18': channelConfiguration(18, trapElectrodeNumber=18),
        # '19': channelConfiguration(6, trapElectrodeNumber=19),
        # '20': channelConfiguration(14, trapElectrodeNumber=20),
        # '21': channelConfiguration(25, trapElectrodeNumber=21),

##    elec_dict = {
##        '01': channelConfiguration(6, trapElectrodeNumber=1),
##        '02': channelConfiguration(27, trapElectrodeNumber=2),
##        '03': channelConfiguration(24, trapElectrodeNumber=3),
##        '04': channelConfiguration(5, trapElectrodeNumber=4),
##        '05': channelConfiguration(14, trapElectrodeNumber=5),
##        '06': channelConfiguration(18, trapElectrodeNumber=6),
##        '07': channelConfiguration(16, trapElectrodeNumber=7),
##        '08': channelConfiguration(13, trapElectrodeNumber=8),
##        '09': channelConfiguration(11, trapElectrodeNumber=9),
##        '10': channelConfiguration(9, trapElectrodeNumber=10), # broken, ground outside
##        '11': channelConfiguration(10, trapElectrodeNumber=11), # broken, ground outside
##        '12': channelConfiguration(7, trapElectrodeNumber=12),
##        '13': channelConfiguration(8, trapElectrodeNumber=13),
##        '14': channelConfiguration(26, trapElectrodeNumber=14),
##        '15': channelConfiguration(25, trapElectrodeNumber=15),
##        '16': channelConfiguration(23, trapElectrodeNumber=16),
##        '17': channelConfiguration(4, trapElectrodeNumber=17),
##        '18': channelConfiguration(19, trapElectrodeNumber=18),
##        '19': channelConfiguration(17, trapElectrodeNumber=19),
##        '20': channelConfiguration(3, trapElectrodeNumber=20),
##        '21': channelConfiguration(20, trapElectrodeNumber=21),
##        '22': channelConfiguration(12, trapElectrodeNumber=22),
##        '23': channelConfiguration(1, trapElectrodeNumber=23), #6
##        '24': channelConfiguration(28, trapElectrodeNumber=29),
##        '25': channelConfiguration(2, trapElectrodeNumber=24),
##        '26': channelConfiguration(3, trapElectrodeNumber=25),
##        '27': channelConfiguration(16, trapElectrodeNumber=27),
##        '28': channelConfiguration(22, trapElectrodeNumber=28)
##        }

        # '01': channelConfiguration(2, trapElectrodeNumber=1),
        # '02': channelConfiguration(3, trapElectrodeNumber=2),
        # '03': channelConfiguration(4, trapElectrodeNumber=3),
        # '04': channelConfiguration(5, trapElectrodeNumber=4),
        # '05': channelConfiguration(9, trapElectrodeNumber=5),
        # '06': channelConfiguration(21, trapElectrodeNumber=6),
        # '07': channelConfiguration(19, trapElectrodeNumber=7),
        # '08': channelConfiguration(6, trapElectrodeNumber=8),
        # '09': channelConfiguration(7, trapElectrodeNumber=9),
        # '10': channelConfiguration(8, trapElectrodeNumber=10), # broken, ground outside
        # '11': channelConfiguration(10, trapElectrodeNumber=11), # broken, ground outside
        # '12': channelConfiguration(22, trapElectrodeNumber=12),
        # '13': channelConfiguration(14, trapElectrodeNumber=13),
        # '14': channelConfiguration(15, trapElectrodeNumber=14),
        # '15': channelConfiguration(16, trapElectrodeNumber=15),
        # '16': channelConfiguration(17, trapElectrodeNumber=16),
        # '17': channelConfiguration(12, trapElectrodeNumber=17),
        # '18': channelConfiguration(13, trapElectrodeNumber=18),
        # '19': channelConfiguration(23, trapElectrodeNumber=19),
        # '20': channelConfiguration(24, trapElectrodeNumber=20),
        # '21': channelConfiguration(25, trapElectrodeNumber=21)