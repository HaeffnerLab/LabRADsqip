import labrad
import time

#servers
cxn = labrad.connect()
dv = cxn.data_vault
dmm = cxn.keithley_2110_dmm()
dmm.select_device(0L)

RESOLUTION = 1.0 # seconds
DURATION = 600. # seconds
NUM_STEPS = int(DURATION / RESOLUTION)

#set up data vault
dv.cd(['','QuickMeasurements','Voltage Measurements'],True)
dv.new('Voltage Scan{}'.format(''),[('Step', '')], [('Voltage','Volts','Volt')] )
dv.add_parameter('plotLive',True)

dat = []

start_time = time.time()

for j in range(NUM_STEPS):
    voltage = dmm.get_dc_volts()
    #voltage = dmm.dc_voltage()
    print j, voltage
    dat.append([j, voltage])
    #dv.add([j,voltage])
    time.sleep(RESOLUTION)
elapsed_time = time.time() - start_time
print 'time taken', elapsed_time
dv.add(dat)

print 'DONE'