#import matplotlib
#matplotlib.use('Qt4Agg')
# from simple_analysis.get_data import *
from sqip_rabi_flop_fitter import *
#from nbar_rabi import *
import scipy.optimize as op
import lmfit
from matplotlib import pyplot
# from U2freqcalc import freq_from_U2

#this is for cycling colors so you can plot in multiple colors and coordinate data points and fits
from itertools import cycle
cycol = cycle('bgrcmk').next 

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

def plot_heating_rate(times,data,err,label='',mycolor='black'):
        #mycolor = cycol()
        pyplot.errorbar(times, data,yerr=err,fmt='o',color=mycolor)
        pyplot.ylabel(r'$\bar{n}$', fontsize=18)
        pyplot.xlabel('time (ms)',fontsize=18)
        def f(x,rate,offset):
                return rate*x+offset
        popt,pcov = op.curve_fit(f,times,data,p0=[1,20],sigma=err)
        

        #variance = cov_matrix[0][0]
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
        excitation_scaling_list = []
        excitation_scaling_errs = []
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
                # N = len(t)/3
                # t = t[0:N]
                # p = p[0:N]
                # perr = perr[0:N]

                #model for Rabi flops, use 0 for sidebands, +-1 etc for sidebands..
                te = rabi_flop_time_evolution(0,eta,nmax=10000) #if you get the error that the hilbert space is too small, then increase nmax
                params = lmfit.Parameters()
                params.add('delta',value = 0.0,vary=False)
                #params.add('delta',value = delta ,vary=True,min=0.01,max=0.04)
                params.add('nbar',value = nbar,min=10.0,max=10000.0)

                if key == 0:
                        params.add('time_2pi',value = time_2pi,vary=True)
                        params.add('excitation_scaling',value = excitation_scaling,vary=True, min=0.9,max=1.0)
                else:
                        params.add('time_2pi',value = time_2pi,vary=False)
                        #params.add('excitation_scaling',value = excitation_scaling,vary=False)
                        params.add('excitation_scaling',value = excitation_scaling,vary=True, min=0.75,max=1.0)
                        
                        
##                params.add('nbar1',value = nbar,min=0.0,max=100.0,vary=True)
##                params.add('nbar2',value = nbar,min=0.0,max=100.0,vary=True)
##              
                guess_values = te.compute_evolution_thermal(params['nbar'].value, params['delta'].value, params['time_2pi'].value, t,params['excitation_scaling'].value)
                
                def rabi_fit_thermal(params,t,data,err):
                        model = te.compute_evolution_thermal(params['nbar'].value, params['delta'].value, params['time_2pi'].value, t,params['excitation_scaling'].value)
                        resid = model-data
                        weighted = [np.sqrt(resid[x]**2/err[x]**2) for x in range(len(err))]
                        # sum_weighted = sum(weighted)
                        # print "sum of residuals: " + str(sum_weighted)
                        return weighted

                def rabi_fit_approx(params,t,data,err):
                        #print params['nbar2'].value                      
                        model = compute_approx_thermal([params['nbar1'].value,params['nbar2'].value], params['time_2pi'].value,etas,t)
                        resid = model-data
                        weighted = [np.sqrt(resid[x]**2/err[x]**2) for x in range(len(err))]
                        return weighted

                if len(etas)<2:
                        result = lmfit.minimize(rabi_fit_thermal,params,method='leastsq',maxfev = 500, xtol = 1.e-7, ftol = 1.e-7, args = (t,p,perr))
                        # print "status" + str(result.status)
                        # print "number of evaluations: " + str(result.nfev)
                        # print "residuals: " + str(result.residual)
                        # print "fit success message: " + str(result.message)
                        # print "least squares message: " + str(result.lmdif_message)
                        print "reduced chi^2 " + str(result.redchi)
                        params = result.params
                        if key == 0:
                                time_2pi = params['time_2pi'].value
                                excitation_scaling = params['excitation_scaling'].value
                        fit_values = te.compute_evolution_thermal(params['nbar'].value, params['delta'].value, params['time_2pi'].value, t, params['excitation_scaling'].value)
                        nbarlist=np.append(nbarlist,params['nbar'].value)
                        nbarerrs=np.append(nbarerrs,params['nbar'].stderr)
                        # print time_2pi

                else:
                        print "approx_thermal"
                        result = lmfit.minimize(rabi_fit_approx,params,args = (t,p,perr))
                        params = result.params
                        if key == 0:
                                time_2pi = params['time_2pi'].value
                                excitation_scaling = params['excitation_scaling'].value
                        fit_values = compute_approx_thermal([params['nbar1'].value,params['nbar2'].value], params['time_2pi'].value,etas,t)
                        nbarlist=np.append(nbarlist,params['nbar1'].value)
                        nbarerrs=np.append(nbarerrs,params['nbar1'].stderr)
                        # print nbarerrs

                #print "nbar fit for " + str(key) + "   " + str(params['nbar'].value) + " +- " + str(params['nbar'].stderr)
                #print "reduced chisquared: " + str(result.redchi)
                #print str(key) + "   " + str(params['time_2pi'].value) + " +- " + str(params['time_2pi'].stderr)         

                pitimes = np.append(pitimes,params['time_2pi'].value/2.0)
                pitimeserr = np.append(pitimeserr,params['time_2pi'].stderr/2.0)
                deltas = np.append(deltas,params['delta'].value)
                deltaserr = np.append(deltaserr,params['delta'].stderr)
                excitation_scaling_list=np.append(excitation_scaling_list,params['excitation_scaling'].value)
                excitation_scaling_errs=np.append(excitation_scaling_errs,params['excitation_scaling'].stderr)
                
                
                if plot_flops:
                        pyplot.figure()
                        mycolor = cycol()
                        pyplot.plot(t,p,'-o',label = 'data ' + str(key),color=mycolor)
                        pyplot.plot(t,fit_values,'r',label = 'fitted '+ str(key),color=mycolor)
                        pyplot.title('flops for trap freq ' + str(int(trap_freq/1000)) + ' kHz')
                        #pyplot.plot(t,guess_values,'r',label = 'guess '+ str(key),color='black')

                        pyplot.legend()
        return (times,nbarlist,nbarerrs,excitation_scaling_list,excitation_scaling_errs)
 

def fit_freq_scaling(freq, rate, rerr,mycolor='b',label=''):
        

        def f(x,Amp,alpha):
                return Amp/x**alpha
        #def f(x,Amp,alpha,offset):
        #        return Amp/x**alpha+offset
        popt,pcov = op.curve_fit(f,freq,rate,p0=[1,2],sigma=rerr)
        #variance = cov_matrix[0][0]
        perr = np.sqrt(np.diag(pcov))
        Amp = popt[0]
        alpha = popt[1]
        #offset = popt[2]
        print popt
        print perr
        #stderr = np.sqrt(variance)
        stderr = perr[1]
        #print "{0:.2f}".format(rate) + ' +- ' + "{0:.2f}".format(stderr) + ' n/ms'
        #print str(rate*1000.)+' n/s'
        
        #pyplot.title('heating rate of ' + "{0:.2f}".format(rate) + ' +- ' + "{0:.2f}".format(stderr) + ' n/ms for trap freq ' + str(int(trap_freq/1000)) + ' kHz')
        freq = np.array(freq)
        rate = np.array(rate)
        rerr = np.array(rerr)
        myorder = np.argsort(freq)
        rate = np.array([rate[x] for x in myorder])
        rerr = np.array([rerr[x] for x in myorder])
        freq = np.array([freq[x] for x in myorder])
        todel = []
        for x in range(len(freq)):
                if freq[x]==freq[x-1]:
                        tmp = [rate[x],rate[x-1]]
                        tmp1 = [rerr[x],rerr[x-1]]
                        lgindx = np.argmax(tmp)
                        newy = (rate[x]+rate[x-1])/2
                        newerr = ((tmp[lgindx]+tmp1[lgindx])-(tmp[lgindx-1]-tmp1[lgindx-1]))/2
                        rate[x-1] = newy
                        rerr[x-1] = newerr
                        rate[x] = newy
                        rerr[x] = newerr
                        todel.append(x)
        for x in todel:
                np.delete(freq,x)
                np.delete(rate,x)
                np.delete(rerr,x)


        pyplot.fill_between(freq, rate-rerr, rate+rerr,facecolor=mycolor,alpha=0.5)
       # pyplot.fill_betweenx(rate,freq-xerr,x+xerr,facecolor='b',alpha=0.5)
        freq = np.sort(freq)
        ratefit = [f(x,Amp,alpha) for x in freq]
        pyplot.plot(freq, ratefit,label=label,color=mycolor)
        return alpha,stderr