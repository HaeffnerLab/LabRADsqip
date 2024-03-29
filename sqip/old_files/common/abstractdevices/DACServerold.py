'''
### BEGIN NODE INFO
[info]
name = DAC Server
version = 1.0
description =
instancename = DAC Server

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20

### END NODE INFO
'''

from labrad.server import LabradServer, setting, Signal, inlineCallbacks
from twisted.internet import reactor
from twisted.internet.defer import returnValue
from scipy import interpolate
from scipy.interpolate import UnivariateSpline as UniSpline
from numpy import *
from numpy import genfromtxt, arange, polynomial
from DacConfiguration import hardwareConfiguration as hc

SERVERNAME = 'DAC Server'
SIGNALID = 270837

class Voltage(object):
    def __init__(self, channel, analogVoltage = None, digitalVoltage = None):
        self.channel = channel
        self.digitalVoltage = digitalVoltage
        self.analogVoltage = analogVoltage
            
    def program(self, setNum):
        '''
        Compute the hex code to progam this voltage
        '''
        self.setNum = setNum
        if self.analogVoltage is not None:
            c = self.channel.calibration
            (vMin, vMax) = self.channel.allowedVoltageRange
            if self.analogVoltage < vMin: self.analogVoltage = vMin
            if self.analogVoltage > vMax: self.analogVoltage = vMax
            #self.digitalVoltage = int(round(sum( [c[n]*self.analogVoltage**n for n in range(len(c)) ] ))) 
            self.digitalVoltage = int(round( polynomial.chebyshev.chebval(self.analogVoltage, c) ))           
        self.hexRep = self.__getHexRep()
        
    def __getHexRep(self):
        '''
        If pulse triggering is enabled in the configuration file,
        then always write set 1 to the DAC. However, still keep track
        of the set numbers to write them in order to the DAC.
        '''
        port = self.__f(self.channel.dacChannelNumber, 5)

        if hc.pulseTriggered: setN = self.__f(self.setNum, 10)
        else: setN = self.__f(1, 10)

        value = self.__f(self.digitalVoltage, 16)
        big = value + port + setN + [False]
        print setN
        return self.__g(big[8:16]) + self.__g(big[:8]) + self.__g(big[24:32]) + self.__g(big[16:24])
            
    def __f(self, num, bits): # binary representation of values in the form of a list
        listy = [False for i in range(bits)]
        for i in range(len(listy)):
            if num >= 2**(len(listy)-i-1):
                listy[i] = True
                num -= 2**(len(listy)-i-1)
        return listy

    def __g(self, listy): # byte to hex
        num = 0
        for i in range(8):
            if listy[i]:
                num += 2**(7-i)
        return chr(num)
        
class Queue(object):
    def __init__(self):
        self.currentSet = 1
        self.setDict = {i: [] for i in range(1, hc.maxCache + 1)}

    def advance(self):
        self.currentSet = (self.currentSet % hc.maxCache) + 1

    def reset(self):
        self.currentSet = 1

    def insert(self, v):
        ''' Always insert voltages to the current queue position '''
        v.program(self.currentSet)
        self.setDict[self.currentSet].append(v)

    def get(self):        
        v = self.setDict[self.currentSet].pop(0)
        return v

class DACServer( LabradServer ):
    """
    DAC Server
    Used for controlling DC trap electrodes
    """
    name = SERVERNAME
    onNewUpdate = Signal(SIGNALID, 'signal: ports updated', 's')
    currentPosition = 0
    registryPath = [ '', 'Servers', hc.EXPNAME + SERVERNAME ]
    
    @inlineCallbacks
    def initServer( self ):
        self.pulser = self.client.pulser
        self.registry = self.client.registry        
        self.dacDict = dict(hc.elecDict.items() + hc.smaDict.items())
        self.queue = Queue()
        self.current = {}
        self.listeners = set() 
        yield self.setCalibrations()
        self.setPreviousVoltages()        
        
    @inlineCallbacks
    def setCalibrations( self ):
        ''' Go through the list of sma outs and electrodes and try to detect calibrations '''
        degreeOfCalibration = 19 # 1st order fit. update this to auto-detect
        yield self.registry.cd(self.registryPath + ['Calibrations'], True)
        subs, keys = yield self.registry.dir()
        sbs = ''
        for s in subs: sbs += s + ', '
        print 'Calibrated channels: ' + sbs
        print self.registryPath + ['Calibrations']
        for chan in self.dacDict.values():
            chan.voltageList = []
            c = [] # list of calibration coefficients in form [c0, c1, ..., cn]
            if str(chan.dacChannelNumber) in subs:
                yield self.registry.cd(self.registryPath + ['Calibrations', str(chan.dacChannelNumber)])
                for n in range( degreeOfCalibration + 1):
                    e = yield self.registry.get( 'c'+str(n) )
                    c.append(e)
                chan.calibration = c
                print chan.dacChannelNumber, chan.calibration
            else:
                (vMin, vMax) = chan.boardVoltageRange
                prec = hc.PREC_BITS
                chan.calibration = [2**(prec - 1), float(2**(prec))/(vMax - vMin) ]

    @inlineCallbacks
    def setPreviousVoltages( self ):
        ''' Get/set previous Cfile, multipole values, and sma voltages from registry '''
        yield self.registry.cd(self.registryPath + ['smaVoltages'], True)
        for k in hc.smaDict.keys():
            try: av = yield self.registry.get(k)
            except: av = 0. # if no previous voltage has been recorded, set to zero. 
            yield self.setIndividualAnalogVoltages(0, [(k, av)])
        # yield self.setIndividualDigitalVoltages(0, [('RF bias', 32768)], 0)
        yield self.registry.cd(self.registryPath)
        try:
            CfilePath = yield self.registry.get('MostRecent')
            yield self.setMultipoleControlFile(0, CfilePath)
        except: 
            self.multipoleMatrix = {k: {j: .1 for j in hc.multipoles} for k in hc.elecDict.keys()} # if no previous Cfile was set, set all entries to zero.
            self.numCols = 1
        try: ms = yield self.registry.get('MultipoleSet')                    
        except: ms = [(k, 0) for k in hc.multipoles] # if no previous multipole values have been recorded, set them to zero. 
        yield self.setMultipoleValues(0, ms)

    @inlineCallbacks
    def sendToPulser(self, c):
        '''
        Send the current queue to the dac
        '''
        self.pulser.reset_fifo_dac()
        for i in range(len(self.queue.setDict[self.queue.currentSet])):
            v = self.queue.get()            
            yield self.pulser.set_dac_voltage(v.hexRep)
            print v.channel.name, v.analogVoltage
            self.current[v.channel.name] = v.analogVoltage
            self.notifyOtherListeners(c)

    def initContext(self, c):
        self.listeners.add(c.ID)

    def expireContext(self, c):
        self.listeners.remove(c.ID)
    
    def notifyOtherListeners(self, context):
        notified = self.listeners.copy()
        try: notified.remove(context.ID)
        except: pass
        self.onNewUpdate('Channels updated', notified)      

    @setting( 0 , "Set Digital Voltages", digitalVoltages = '*v', setNum = 'i', returns = '')
    def setDigitalVoltages( self, c, digitalVoltages, setNum):
        """
        Pass digitalVoltages, a list of digital voltages to update.
        Currently, there must be one for each port.
        """
        l = zip(range(1, hc.numDacChannels + 1), digitalVoltages)
        self.setIndivDigVoltages(c, l, setNum)

    @setting( 1 , "Set Analog Voltages", analogVoltages = '*v', setNum = 'i', returns = '')
    def setAnalogVoltages( self, c, analogVoltages, setNum):
        """
        Pass analogVoltages, a list of analog voltages to update.
        Currently, there must be one for each port.
        """
        l = zip(range(1, hc.numDacChannels + 1), analogVoltages)
        yield self.setIndivAnaVoltages(c, l, setNum)

    @setting( 2, "Set Individual Digital Voltages", digitalVoltages = '*(si)', returns = '')
    def setIndividualDigitalVoltages(self, c, digitalVoltages, setNum = 0):
        """
        Pass a list of tuples of the form:
        (portNum, newVolts)
        """
        for (port, dv) in digitalVoltages:
            self.queue.insert(Voltage(self.dacDict[port], digitalVoltage = dv))
        yield self.sendToPulser(c)

    @setting( 3, "Set Individual Analog Voltages", analogVoltages = '*(sv)', returns = '')
    def setIndividualAnalogVoltages(self, c, analogVoltages):
        """
        Pass a list of tuples of the form:
        (portNum, newVolts)
        """
        for (port, av) in analogVoltages:
            self.queue.insert(Voltage(self.dacDict[port], analogVoltage = av))
            if self.dacDict[port].smaOutNumber:
                self.registry.cd(self.registryPath + ['smaVoltages'])
                self.registry.set(port, av)
        yield self.sendToPulser(c)

    @setting( 4, "Get Analog Voltages", returns = '*(sv)' )
    def getCurrentVoltages(self, c):
        """
        Return the current voltage
        """
        return self.current.items()
    
    @setting( 5, "Set Multipole Control File", CfilePath = 's')
    def setMultipoleControlFile(self, c, CfilePath):                
        data = genfromtxt(CfilePath)
        self.numCols = data[1].size
        if self.numCols == 1: 
            self.multipoleMatrix = {elec: {mult: data[int(elec) + index*hc.numElectrodes - 1] for index, mult in enumerate(hc.multipoles)} for elec in hc.elecDict.keys()}
            self.positionList = data[-1]
        else: self.interpolateMultipoleMatrix(data)

        yield self.registry.cd(self.registryPath)
        yield self.registry.set('MostRecent', CfilePath)

    def interpolateMultipoleMatrix( self, data ):
        ''' fit individual components of multiple Cfiles to a spline '''
        numElectrodes = (data[:,1].size - 1) / len(hc.multipoles)
        numPositions = 10*(self.numCols - 1.)
        inc = (self.numCols-1)/numPositions
        partition = arange(0, (numPositions + 1) * inc, inc)
        splineFit = {elec: {mult: UniSpline(range(self.numCols) , data[int(elec) + index*hc.numElectrodes - 1], s = 0 ) for index, mult in enumerate(hc.multipoles)} for elec in hc.elecDict.keys()}
        self.multipoleMatrix = {elec: {mult: splineFit[elec][mult](partition) for index, mult in enumerate(hc.multipoles)} for elec in hc.elecDict.keys()}
        positionFit = interpolate.interp1d(range(self.numCols) , data[numElectrodes * len(hc.multipoles)], 'linear')
        self.positionList = positionFit(partition)

    @setting( 6, "Set Multipole Values", ms = '*(sv): dictionary of multipole values')
    def setMultipoleValues(self, c, ms):
        """
        set should be a dictionary with keys 'Ex', 'Ey', 'U2', etc.
        """
        self.multipoleSet = {}
        for (k,v) in ms:
            self.multipoleSet[k] = v
        yield self.setVoltages(c, self.currentPosition)

        yield self.registry.cd(self.registryPath)
        yield self.registry.set('MultipoleSet', ms)

    @setting( 7, "Get Multipole Values",returns='*(s,v)')
    def getMultipoleValues(self, c):
        """
        Return a list of multipole voltages
        """
        return self.multipoleSet.items()
                        
    @setting( 8, "Set Voltages", newPosition = 'i')
    def setVoltages(self, c, newPosition = currentPosition):
        n = newPosition
        newVoltageSet = []
        # apply multipole matrix to multipole vector
        for e in hc.elecDict.keys():        
            av = 0
            for m in hc.multipoles:                 
                if self.numCols == 1: av += self.multipoleMatrix[e][m] * self.multipoleSet[m] # numpy.0-dimnl_array[0] throws error
                else: av += self.multipoleMatrix[e][m][n] * self.multipoleSet[m] # numpy.array[0] = scalar
            newVoltageSet.append( (e, av) )
        # if changing DAC FPGA voltage set, write sma voltages. 
        #if advance or reset:
        #    for s in hc.smaDict.keys():
        #        newVoltageSet.append( (s, self.current[s]) )
        yield self.setIndividualAnalogVoltages(c, newVoltageSet)
        self.currentPosition = n
        
        print self.queue.currentSet

    @setting( 9, "Set First Voltages")
    def setFirstVoltages(self, c):
        self.queue.reset()
        yield self.setVoltages(c)

    @setting( 10, "Set Next Voltages", newPosition = 'i')
    def setFutureVoltages(self, c, newPosition):
        self.queue.advance()
        yield self.setVoltages(c, newPosition = newPosition)        
    
    @setting( 11, "Get Position", returns = 'i')
    def getPosition(self, c):
        return self.currentPosition
                
    @setting( 12, "Set Next U2", U2 = 'v')
    def setNextU2(self, c, U2):
        self.multipoleSet['U2'] = U2
        self.queue.advance()
        yield self.setVoltages(c)
        
    @setting( 13, "Set Voltage",  analogVoltages = '*(sv)',returns ='')
    def setVoltage(self, c, analogVoltages):
        self.queue.advance()
        yield self.setVoltages(c)
        self.setIndividualAnalogVoltages(c,analogVoltages)
        
    @setting( 14, 'Reset Queue')
    def resetQueue(self, c):
        self.queue.reset()
                
if __name__ == "__main__":
    from labrad import util
    util.runServer( DACServer() )

"""
Notes for setting up DACSERVER:

example of a Cfile corresponding to a trap w/ 23 electrodes, 4 multipole values, and trap position of 850um:

Ex_1
Ex_2
.
.
.
Ex_23
Ey_1
.
.
.
U2_23
850

Be sure to specify multipole names in DacCanfiguration.py, e.g., multipoles = ['Ex', Ey', 'Ez', 'U2'].


or, if you intend to do shuttling, place Cfiles next to each other:
Ex_1.1   Ex_1.2
Ex_2.1   Ex_2.2
.        .
.        .
.        .
Ex_23.1  .
Ey_1.1   .
.        .
.        .
.        .
U2_23.1  U2_23.2
850      900
"""