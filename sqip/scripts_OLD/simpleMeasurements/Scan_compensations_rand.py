import labrad
import time
import numpy as np
import itertools
import random
cxn = labrad.connect()
dc = cxn.dac_server()

fields = dict(dc.get_multipole_values())

Ex_ar = np.arange(-3.0, 4., 1.)
Ey_ar = np.arange(-3.0, 4., 1.)

comps = []

for i, j in itertools.product(Ex_ar, Ey_ar):
    comps.append((i, j))
    
wait = 10.
print 'Running...' , len(comps)

while 1:
    current_comp = random.choice(comps)
    print 'Current Ex, Ey : ', current_comp
    fields['Ex'] = current_comp[0]
    fields['Ey'] = current_comp[1]
    dc.set_multipole_values(fields.items())
    comps.remove(current_comp)
    print 'Time remaining : ', wait*len(comps)/60., 'minutes'
    time.sleep(wait)
    