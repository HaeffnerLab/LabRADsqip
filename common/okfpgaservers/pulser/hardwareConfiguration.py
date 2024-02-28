class channelConfiguration(object):
    """
    Stores complete configuration for each of the channels
    """
    def __init__(self, channelNumber, ismanual, manualstate,  manualinversion, autoinversion):
        self.channelnumber = channelNumber
        self.ismanual = ismanual
        self.manualstate = manualstate
        self.manualinv = manualinversion
        self.autoinv = autoinversion
        
class ddsConfiguration(object):
    """
    Stores complete configuration of each DDS board
    """
    def __init__(self, address, allowedfreqrange, allowedamplrange, frequency, amplitude, **args):
        self.channelnumber = address
        self.allowedfreqrange = allowedfreqrange
        self.allowedamplrange = allowedamplrange
        self.frequency = frequency
        self.amplitude = amplitude
        self.state = True
        self.boardfreqrange = args.get('boardfreqrange', (0.0, 800.0))
        self.boardamplrange = args.get('boardamplrange', (-63.0, -3.0))
        self.boardphaserange = args.get('boardphaserange', (0.0, 360.0))
        self.off_parameters = args.get('off_parameters', (0.0, -63.0))
        self.phase_coherent_model = args.get('phase_coherent_model', True)        
        self.remote = args.get('remote', False)
        self.name = None #will get assigned automatically

class remoteChannel(object):
    def __init__(self, ip, server, **args):
        self.ip = ip
        self.server = server
        self.reset = args.get('reset', 'reset_dds')
        self.program = args.get('program', 'program_dds')
        
class hardwareConfiguration(object):
    channelTotal = 32
    timeResolution = '40.0e-9' #seconds
    timeResolvedResolution = 10.0e-9
    maxSwitches = 1022
    resetstepDuration = 2 #duration of advanceDDS and resetDDS TTL pulses in units of timesteps
    collectionTimeRange = (0.0001, 5.0) #range for normal pmt counting
    sequenceTimeRange = (0.0, 85.0) #range for duration of pulse sequence    
    isProgrammed = False
    sequenceType = None #none for not programmed, can be 'one' or 'infinite'
    collectionMode = 'Normal' #default PMT mode
    collectionTime = {'Normal':0.100,'Differential':0.100} #default counting rates
    okDeviceID = 'Pulser'
    okDeviceFile = 'pulser_2013_06_05.bit'
    lineTriggerLimits = (0, 15000)#values in microseconds 
    secondPMT = False
    DAC = True
    
    #name: (channelNumber, ismanual, manualstate,  manualinversion, autoinversion)  First 3 are for manual state setting
    channelDict = {
                   '866DP':channelConfiguration(13,   False, True, True, True),
                   'bluePI':channelConfiguration(2,   True, False, True, False),
                   '854DP':channelConfiguration(3,   True, True, False, False),
                   'Optical4':channelConfiguration(4,   False, True, True, True),
                   'Optical5':channelConfiguration(5,   False, True, True, True),
		   'Optical6':channelConfiguration(6,   True, True, False, False),
		   'Optical7':channelConfiguration(7,   True, True, False, False),
		   'Optical8':channelConfiguration(8,   True, True, False, False),
		   'Optical9':channelConfiguration(9,   True, True, False, False),
		   'adv':channelConfiguration(10, False,False,False,False),
		   'rst':channelConfiguration(11, False,True,True,True),
		   'TTL0':channelConfiguration(     12, False, True, False, True),
		   'TTL1':channelConfiguration(     1, True, True, False, False),
		   'TTL2':channelConfiguration(     14, True, True, False, False),
		   'TTL3':channelConfiguration(     15, True, True, False, False),
                   #------------INTERNAL CHANNELS----------------------------------------#
                   'Internal866':channelConfiguration(        0, False, False, False, False),
                   'DiffCountTrigger':channelConfiguration(  16, False, False, False, False),
                   'TimeResolvedCount':channelConfiguration( 17, False, False, False, False),
                   'AdvanceDDS':channelConfiguration(        18, False, False, False, False),
                   'ResetDDS':channelConfiguration(          19, False, False, False, False),
                   'ReadoutCount':channelConfiguration(      20, False, False, False, False),
                }
    #address, allowedfreqrange, allowedamplrange, frequency, amplitude, **args):
    ddsDict =   {
                '397DP':ddsConfiguration(    0,  (70.0, 250.0),   (-63.0, -5.0),   220.0,  -63.0),
                '866DP':ddsConfiguration(    1,  ( 70.0,  250.0),   (-63.0, -3.0),    80.0,  -63.0),
                '729DP':ddsConfiguration(    2,  (150.0,250.0),   (-63.0, -3.0),   200.0,  -63.0),
                '854DP':ddsConfiguration(    3,  ( 70.0,  90.0),   (-63.0, -3.0),    90.0,  -63.0),
                'SPARE':ddsConfiguration(    4,  ( 70.0,  90.0),   (-63.0, -5.0),   80.0,  -63.0),
                }
    remoteChannels = {
                    }
