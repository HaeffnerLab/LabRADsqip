'''
To apply voltages to DAC electrodes during Ar+ cleaning.  Voltages alternate between +ve and -ve on adjacent electrodes
'''
import labrad
import time
from common.okfpgaservers.dacserver.DacConfiguration import hardwareConfiguration as hc
cxn = labrad.connect()
dac = cxn.dac_server()

volt_range = 9.8
wait = 10 # in seconds

numElectrodes = len(hc.elec_dict)
print numElectrodes

def neg((a,b)):
    if b%2:return a
    else:return -1.0*a
    
electrodes = ['RF bias'] + ['0' + str(j) for j in range(1, 10)] + ([str(j) for j in range(10, numElectrodes + 1)])
print electrodes
k = 1   
var = 1

#for run in range(iters)
while(var == 1):
    k = -1.0*k
    voltages = [k*volt_range*float(j) for j in [1] * (numElectrodes + 1)]
    voltages = map(neg,zip(voltages,range(len(voltages))))
    lst = zip(electrodes, voltages)
    dac.set_individual_analog_voltages(lst)
    time.sleep(wait)