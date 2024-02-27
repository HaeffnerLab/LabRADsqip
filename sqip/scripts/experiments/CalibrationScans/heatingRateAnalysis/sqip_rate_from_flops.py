#import matplotlib
#matplotlib.use('Qt4Agg')
# from simple_analysis.get_data import *
from sqip_rabi_flop_fitter import *
#from nbar_rabi import *
import scipy.optimize as op
import lmfit
from matplotlib import pyplot
# from U2freqcalc import freq_from_U2
import numpy as np

#this is for cycling colors so you can plot in multiple colors and coordinate data points and fits
from itertools import cycle
cycol = cycle('bgrcmk').next

######
## Note: the only function in here that is updated to include excitation scaling is
## the fit single flop function. 09/14
## Corrected the division by zero in the fit procedure. 09/21
####

hbar = 1.0546e-34
m = 39.96*1.66e-27

def import_data(filename):
	t,p = np.loadtxt(filename,unpack=True, delimiter=',')
	return t,p

def calc_eta(trap_freq,theta):
        theta = np.deg2rad(theta)
        return 2*np.pi/729.e-9*np.sqrt(hbar/(2*m*2*np.pi*trap_freq))*np.cos(theta)

def compute_approx_thermal(nbars,time_2pi,etas,t):
        omega = np.pi/time_2pi
        scaling = sum([etas[i]**2*nbars[i] for i in range(len(nbars))])
        Qfunc = [np.exp(2j*omega*x)/(1+1j*omega*x*scaling) for x in t]
        return [0.5*(1-np.real(x)) for x in Qfunc]

def plot_heating_rate(times,data,err,label=''):
        mycolor = cycol()
        pyplot.errorbar(times, data,yerr=err,fmt='o',color=mycolor)
        pyplot.ylabel(r'$\bar{n}$', fontsize=18)
        pyplot.xlabel('time (ms)',fontsize=18)
        def f(x,rate,offset):
                return rate*x+offset
        popt,pcov = op.curve_fit(f,times,data,p0=[1,20],sigma=err)
        #variance =
        te = rabi_flop_time_evolution(0,eta,nmax=2500) #if you get the error that the hilbert space is too small, then increase nmax
        #cov_matrix[0][0]
        perr = np.sqrt(np.diag(pcov))
        rate = popt[0]
        offset = popt[1]
        #print popt
        #print perr
        #stderr = np.sqrt(variance)
        stderr = perr[0]
        #print "{0:.2f}".format(rate) + ' +- ' + "{0:.2f}".format(stderr) + ' n/ms'
        #print str(rate*1000.)+' n/s'
        times = np.sort(times)
        pyplot.plot(times, rate*times+offset,label=label,color=mycolor)
        #pyplot.title('heating rate of ' + "{0:.2f}".format(rate) + ' +- ' + "{0:.2f}".format(stderr) + ' n/ms for trap freq ' + str(int(trap_freq/1000)) + ' kHz')
        return rate,stderr

def fit_rabi_flops(file_loc,file_ext,data_dict,trap_freq,plot_flops,excitation_scaling,time_2pi,nbar,etas,delta):
        nbarlist = []
        nbarerrs = []
        pitimes = []
        pitimeserr = []
        deltas = []
        deltaserr = []
        # if plot_flops:
                # pyplot.figure()
        #this part does the rabi flop fitting for each data set
        times = np.sort(data_dict.keys())
        eta = etas[0]
        for key in times:
                #import data and calculate errors based on 100 experiments
                t,p = import_data(file_loc + str(data_dict[key][0]) + ".dir/" + file_ext + str(data_dict[key][0]) + ".csv")
                perr = [np.sqrt(x*(1-x)/100.) for x in p]
                for index in range(0,len(p)):
                        if perr[index] == 0:
                                perr[index] = np.sqrt(0.01*(1-0.01)/100.)
                #model for Rabi flops, use 0 for sidebands, +-1 etc for sidebands..
                te = rabi_flop_time_evolution(0,eta,nmax=2500) #if you get the error that the hilbert space is too small, then increase nmax
                params = lmfit.Parameters()
                params.add('delta',value = 0.0,vary=False)
                #params.add('delta',value = delta ,vary=True,min=0.01,max=0.04)
                params.add('nbar',value = nbar,min=0.0,max=200.0)

                if key == 0:
                        params.add('time_2pi',value = time_2pi,vary=True)
                else:
                        params.add('time_2pi',value = time_2pi,vary=False)
                        
##                params.add('nbar1',value = nbar,min=0.0,max=100.0,vary=True)
##                params.add('nbar2',value = nbar,min=0.0,max=100.0,vary=True)
##
                
                def rabi_fit_thermal(params,t,data,err):
                        model = te.compute_evolution_thermal(params['nbar'].value, params['delta'].value, params['time_2pi'].value, t,excitation_scaling=excitation_scaling)
                        resid = model-data
                        weighted = [np.sqrt(resid[x]**2/err[x]**2) for x in range(len(err))]
                        return weighted

                def rabi_fit_approx(params,t,data,err):
                        #print params['nbar2'].value                      
                        model = compute_approx_thermal([params['nbar1'].value,params['nbar2'].value], params['time_2pi'].value,etas,t)
                        resid = model-data
                        weighted = [np.sqrt(resid[x]**2/err[x]**2) for x in range(len(err))]
                        return weighted

                if len(etas)<2:
                        result = lmfit.minimize(rabi_fit_thermal,params,args = (t,p,perr))
                        params = result.params
                        if key == 0:
                                time_2pi = params['time_2pi'].value
                        fit_values = te.compute_evolution_thermal(params['nbar'].value, params['delta'].value, params['time_2pi'].value, t)
                        nbarlist=np.append(nbarlist,params['nbar'].value)
                        nbarerrs=np.append(nbarerrs,params['nbar'].stderr)

                else:
                        result = lmfit.minimize(rabi_fit_approx,params,args = (t,p,perr))
                        params = result.params
                        if key == 0:
                                time_2pi = params['time_2pi'].value
                        fit_values = compute_approx_thermal([params['nbar1'].value,params['nbar2'].value], params['time_2pi'].value,etas,t)
                        nbarlist=np.append(nbarlist,params['nbar1'].value)
                        nbarerrs=np.append(nbarerrs,params['nbar1'].stderr)
                        print nbarerrs

                #print "nbar fit for " + str(key) + "   " + str(params['nbar'].value) + " +- " + str(params['nbar'].stderr)
                #print "reduced chisquared: " + str(result.redchi)
                #print str(key) + "   " + str(params['time_2pi'].value) + " +- " + str(params['time_2pi'].stderr)         

                pitimes = np.append(pitimes,params['time_2pi'].value/2.0)
                pitimeserr = np.append(pitimeserr,params['time_2pi'].stderr/2.0)
                deltas = np.append(deltas,params['delta'].value)
                deltaserr = np.append(deltaserr,params['delta'].stderr)
                
                if plot_flops:
                        pyplot.figure()
                        mycolor = cycol()
                        pyplot.plot(t,p,'-o',label = 'data ' + str(key),color=mycolor)
                        pyplot.plot(t,fit_values,'r',label = 'fitted '+ str(key),color=mycolor)
                        pyplot.title('flops for trap freq ' + str(int(trap_freq/1000)) + ' kHz')
                        pyplot.legend()
        return (times,nbarlist,nbarerrs)


def alt_fit_rabi_flops(times, ts, ps, trap_freq,time_2pi,eta):
	delta = 0  
	excitation_scaling=1 
	plot_flops=False
	nbar = 40     
	nbarlist = []
        nbarerrs = []
        pitimes = []
        pitimeserr = []
        deltas = []
        deltaserr = []
        # if plot_flops:
                # pyplot.figure()
        #this part does the rabi flop fitting for each data set
 
        for index in range(len(times)):
                #import data and calculate errors based on 100 experiments
                key = times[index]
		t=ts[index]
		p=ps[index]
                p[0] = 0.001 #there is something wrong with the first entry and this solves it?
                perr = [np.sqrt(x*(1-x)/100.) for x in p]
                #model for Rabi flops, use 0 for sidebands, +-1 etc for sidebands..
                te = rabi_flop_time_evolution(0,eta,nmax=2500) #if you get the error that the hilbert space is too small, then increase nmax
                params = lmfit.Parameters()
                params.add('delta',value = 0.0,vary=False)
                #params.add('delta',value = delta ,vary=True,min=0.01,max=0.04)
                params.add('nbar',value = nbar,min=0.0,max=200.0)

                if key == 0:
                        params.add('time_2pi',value = time_2pi,vary=True)
                else:
                        params.add('time_2pi',value = time_2pi,vary=False)
                        
##                params.add('nbar1',value = nbar,min=0.0,max=100.0,vary=True)
##                params.add('nbar2',value = nbar,min=0.0,max=100.0,vary=True)
##
                
                def rabi_fit_thermal(params,t,data,err):
                        model = te.compute_evolution_thermal(params['nbar'].value, params['delta'].value, params['time_2pi'].value, t,excitation_scaling=excitation_scaling)
                        resid = model-data
                        weighted = [np.sqrt(resid[x]**2/err[x]**2) for x in range(len(err))]
                        return weighted

                

                result = lmfit.minimize(rabi_fit_thermal,params,args = (t,p,perr))
                params = result.params
                if key == 0:
                	time_2pi = params['time_2pi'].value
                fit_values = te.compute_evolution_thermal(params['nbar'].value, params['delta'].value, params['time_2pi'].value, t)
                nbarlist=np.append(nbarlist,params['nbar'].value)
                nbarerrs=np.append(nbarerrs,params['nbar'].stderr)

                if plot_flops:
                        pyplot.figure()
                        mycolor = cycol()
                        pyplot.plot(t,p,'-o',label = 'data ' + str(key),color=mycolor)
                        pyplot.plot(t,fit_values,'r',label = 'fitted '+ str(key),color=mycolor)
                        pyplot.title('flops for trap freq ' + str(int(trap_freq/1000)) + ' kHz')
                        pyplot.legend()
        return (times,nbarlist,nbarerrs)

def sqip_fit_single_flop(key,t,p, trap_freq,time_2pi,eta,excitation_scaling,sideband_order=0):
	#delta = 0  
	#excitation_scaling=1.0 
	nbar = 20.0     
	
        perr = np.array([np.sqrt(x*(1-x)/100.) for x in p])
        for index in range(0,len(p)):
                if perr[index] == 0:
                        perr[index] = np.sqrt(0.01*(1-0.01)/100.)
        #model for Rabi flops, use 0 for sidebands, +-1 etc for sidebands..
        te = rabi_flop_time_evolution(sideband_order,eta,nmax=6000) #if you get the error that the hilbert space is too small, then increase nmax
        params = lmfit.Parameters()
        params.add('delta',value = 0.0,vary=False)
        params.add('nbar',value = nbar,min=0.01,max=200.0)

        if key == 0:
                params.add('time_2pi',value = time_2pi,vary=True)
                params.add('excitation_scaling',value = excitation_scaling,vary=True, min=0.95,max=1.0)
                #params.add('excitation_scaling',value = excitation_scaling,vary=False)

        else:
                params.add('time_2pi',value = time_2pi,vary=False)
                #params.add('excitation_scaling',value = excitation_scaling,vary=False)
                params.add('excitation_scaling',value = excitation_scaling,vary=True, min=0.95,max=1.0)


##        params.add('time_2pi',value = time_2pi,vary=False)
##        params.add('excitation_scaling',value = excitation_scaling,vary=False)        
        def rabi_fit_thermal(params,t,data,err):
                model = te.compute_evolution_thermal(params['nbar'].value, params['delta'].value, params['time_2pi'].value, t,params['excitation_scaling'].value)
                resid = model-data
                weighted = [np.sqrt(resid[x]**2/err[x]**2) for x in range(len(err))]
                return np.array(weighted)

        print params
        result = lmfit.minimize(rabi_fit_thermal,params,args = (t,p,perr))
        print result.params
        params = result.params
##        if key == 0:
##                time_2pi = params['time_2pi'].value

##        fit_values = te.compute_evolution_thermal(params['nbar'].value, params['delta'].value, params['time_2pi'].value, t)

        print 'in sqipratefromflops'
        print params['nbar'].stderr
        return params['nbar'].value,params['nbar'].stderr, params['time_2pi'].value,params['excitation_scaling'].value
 
