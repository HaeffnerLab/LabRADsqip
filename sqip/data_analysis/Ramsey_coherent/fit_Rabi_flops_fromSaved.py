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
info = ('Carrier Flops', ('2014May27','1706_02')); alpha_guess = 0.0;
trap_frequency = WithUnit(0.817, 'MHz') 
projection_angle = 7 #degrees
offset_time = 0
sideband_order = 0
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
params.add('nbar', value = 23, min = 0.0, max = 200.0, vary = True)
params.add('alpha', value = alpha_guess, min = 0.0, max = 200.0, vary = False)
'''
#load the dataset
'''
def get_data(dataSet):
    os.chdir('Z:\\SQIP\\Data\\05272014')
    print os.getcwd()   
    times, prob = np.load(dataSet) #'1711_56.npy'
    tmin,tmax = times.min(), times.max()
    detailed_times = np.linspace(tmin, tmax, 1000)
    return [times, prob, tmin, tmax, detailed_times]

title,dataset = info 
date,datasetName = dataset
[times, prob,tmin, tmax, detailed_times] = get_data(info[1][1] + '.npy')
U2 = 5.0    
trap_frequency = 0.817*np.sqrt(U2/5.) # in MHz 
SAVE = 1


'''
# compute time evolution of the guessed parameters
'''
guess_evolution = flop.compute_evolution_coherent(params['nbar'].value , params['alpha'].value, params['detuning'].value, params['time_2pi'].value, detailed_times - offset_time, excitation_scaling = params['excitation_scaling'].value)

'''
# define how to compare data to the function
'''
def rabi_flop_fit_thermal(params , t, data):
    model = flop.compute_evolution_coherent(params['nbar'].value , params['alpha'].value, params['detuning'].value, params['time_2pi'].value, t - offset_time, excitation_scaling = params['excitation_scaling'].value)
    return model - data
'''
# perform the fit
'''
region = (fitting_region[0] <= times) * (times <= fitting_region[1]) 
result = lmfit.minimize(rabi_flop_fit_thermal, params, args = (times[region], prob[region]))
fit_values = flop.compute_evolution_coherent(params['nbar'].value , params['alpha'].value, params['detuning'].value, params['time_2pi'].value, detailed_times - offset_time, excitation_scaling = params['excitation_scaling'].value)
#lmfit.report_errors(params)

'''
# make the plot
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
    figname = datasetName + '.png'
    pylab.savefig(figname)
    analyzed = {'detailed_times' : detailed_times,
                'fit_values' : fit_values
                }
    with open(datasetName + "_analyzed.csv", "a") as fh:
        fh.write(#'dict = ' + repr(analyzed) + '\n' ,
                str([ params['nbar'].value, params['alpha'].value]).strip('[]') + '\n') 
    fh.close()
    
pyplot.show()

