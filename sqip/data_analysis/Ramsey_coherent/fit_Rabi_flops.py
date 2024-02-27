import lmfit
import labrad
from labrad.units import WithUnit
import os
from rabi_flop_fitter.lamb_dicke import lamb_dicke
from rabi_flop_fitter.rabi_flop_fitter import rabi_flop_time_evolution
import numpy as np
from matplotlib import pyplot
import pylab

'''
script parameters
'''
info = ('Carrier Flops', ('2014May27','1711_56')); alpha_guess = 5.0;
trap_frequency = WithUnit(0.817, 'MHz') 
projection_angle = 7 #degrees
offset_time = 0
sideband_order = 2
fitting_region = (1, 60) #microseconds
'''
compute lamb dicke parameter
'''
eta = lamb_dicke.lamb_dicke(trap_frequency, projection_angle)
print 'Lamb Dicke parameter: {0:.2f}'.format(eta)
'''
initialize the fitter
'''
flop = rabi_flop_time_evolution(sideband_order, eta)
'''
create fitting parameters
'''
params = lmfit.Parameters()
params.add('excitation_scaling', value = 0.98, vary = False)
params.add('detuning', value = 0, vary = False) #units of rabi frequency
params.add('time_2pi', value = 45, vary = False) #microseconds
params.add('nbar', value = 23, min = 0.0, max = 200.0, vary = False)
params.add('alpha', value = alpha_guess, min = 0.0, max = 200.0, vary = True)
'''
#load the dataset
'''
dv = labrad.connect().data_vault
title,dataset = info 
date,datasetName = dataset
dv.cd( ['','Experiments','RabiFloppingKicked',date,datasetName] )
dv.open(1)  
times,prob = dv.get().asarray.transpose()
tmin,tmax = times.min(), times.max()
detailed_times = np.linspace(tmin, tmax, 1000)
wait = dv.get_parameter('Heating.background_heating_time')
try:
    U2 = dv.get_parameter('Multipole.U2')
    print '\n U2 is: ', U2 
except Exception as e:
    U2 = 5.0
    print '\n\n No data vault parameter "U2"; using user-supplied U2 = ', U2 
trap_frequency = 0.817*np.sqrt(U2/5.) # in MHz 
SAVE = 0

'''
compute time evolution of the guessed parameters
'''
guess_evolution = flop.compute_evolution_coherent(params['nbar'].value , params['alpha'].value, params['detuning'].value, params['time_2pi'].value, detailed_times - offset_time, excitation_scaling = params['excitation_scaling'].value)

'''
define how to compare data to the function
'''
def rabi_flop_fit_thermal(params , t, data):
    model = flop.compute_evolution_coherent(params['nbar'].value , params['alpha'].value, params['detuning'].value, params['time_2pi'].value, t - offset_time, excitation_scaling = params['excitation_scaling'].value)
    return model - data
'''
perform the fit
'''
region = (fitting_region[0] <= times) * (times <= fitting_region[1])
result = lmfit.minimize(rabi_flop_fit_thermal, params, args = (times[region], prob[region]))
fit_values = flop.compute_evolution_coherent(params['nbar'].value , params['alpha'].value, params['detuning'].value, params['time_2pi'].value, detailed_times - offset_time, excitation_scaling = params['excitation_scaling'].value)
#lmfit.report_errors(params)

'''
make the plot
'''
pyplot.figure()
# pyplot.plot(detailed_times, guess_evolution, '--k', alpha = 0.5, label = 'initial guess')
pyplot.plot(times, prob, 'ob', label = 'data')
pyplot.plot(detailed_times, fit_values, 'r', label = 'fitted')
# pyplot.plot(detailed_times, y_values, 'b', label = 'simplified')

pyplot.legend()
pyplot.title(title, fontsize = 16)
pyplot.xlabel('time (us)', fontsize = 16)
pyplot.ylabel('D state occupation probability', fontsize = 16)
pyplot.annotate('detuning = {0}'.format(params['detuning'].value), (0.55,0.30), xycoords = 'figure fraction', fontsize = 16)
pyplot.annotate('nbar = {:.1f}'.format(params['nbar'].value), (0.55,0.25), xycoords = 'figure fraction', fontsize = 16)
pyplot.annotate('2 Pi Time = {:.1f} us'.format(params['time_2pi'].value), (0.55,0.20), xycoords = 'figure fraction', fontsize = 16)
pyplot.annotate('alpha = {0:.1f}'.format(params['alpha'].value), (0.55,0.15), xycoords = 'figure fraction', fontsize = 16)
pyplot.tick_params(axis='both', which='major', labelsize=16)
pyplot.tight_layout()
pyplot.xlim([0,100])
pyplot.ylim([0,1.0])
if SAVE:
    os.chdir('Z:\\SQIP\\Data\\05272014')
    print os.getcwd()
    figname = 'U2_' + str(U2) + '_t=' + str(wait) + '.png'
    pylab.savefig(figname)
    with open("U2_" + str(U2) + "data_file.csv", "a") as fh:
        fh.write(str([float(str(wait).strip(' ms')), params['nbar'].value, params['alpha'].value]).strip('[]') + '\n') 
    fh.close()
    
pyplot.show()

