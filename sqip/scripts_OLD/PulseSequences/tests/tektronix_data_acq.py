from labrad.units import WithUnit
from common.okfpgaservers.pulser.pulse_sequences.plot_sequence import SequencePlotter

from Impulse_test import main
import time
'''
Created on Jul 8, 2013

@author: expcontrol
'''

if __name__ == '__main__':
    import labrad
    cxn = labrad.connect()
    tek = cxn['tektronix_server']
    v = tek.list_devices()[0][1]
    print v
    from time import sleep
    tek.select_device(v)
    tek.setchannel(2)
   
    resp= '1'
    tot = '1'
    totcount =0
    iters = 0
    rep = 5
    numiter= 100
    for i in range(1,rep+1):
        main()
        sleep(1)
        iters = 0
        strlist = []
        strlist.append('transfer100iter')
        strlist.append(str(i))
        strlist.append('.txt')
        name=''.join(strlist)
        
        for i4 in range(1,numiter+1):
            i2 = 0
            rr = tek.getcurve()
            totcount = totcount+1
            iters = iters+1
            if(i4 ==1):
                resp = rr
                if(i==1):
                    tot = rr
            while i2 < len(resp):
                if(i4 != 1):
                    resp[i2][0] = resp[i2][0] + rr[i2][0]
                    resp[i2][1] = resp[i2][1] + rr[i2][1]
                if(i != 1 and i4 != 1):
                    tot[i2][0] = tot[i2][0] + rr[i2][0]
                    tot[i2][1] = tot[i2][1] + rr[i2][1]
                i2 = i2+1
            print iters
        cxn.pulser.wait_sequence_done()
        cxn.pulser.stop_sequence()
        #f = open(name,'w')
        #f.truncate()
        #for item in resp:
        #    print>>f,item[0]/iters,item[1]/iters
        #f.close()
        
    f = open('transfer100iter.txt','w')
    f.truncate()
    for item in tot:
        print>>f,item[0]/totcount,item[1]/totcount
    f.close()
    print 'finished'
    
