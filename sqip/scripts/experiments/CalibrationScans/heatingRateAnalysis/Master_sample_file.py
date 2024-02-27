from sqip_rate_from_flops import *
import os

#parameters inserted into calculation
trap_freq = 0.631*1e6 #in Hz
nbar = 10 #guess for nbar
excitation_scaling=1.0 #change this if OP not working
plot_flops=True #set to true to plot the flops
theta=11.5 #the0 angle of the laser with the trap axis
time_2pi=40 #guess for 2pi time in microseconds

etas = [calc_eta(trap_freq,theta)]
delta={}
current_dir=os.getcwd()
#data without ramping
file_loc = current_dir + "/2017_08_08 heating rates/"
file_ext = "00001 - Rabi Flopping 2017Aug08_"
data_dict = {} #keys are the wait time in


data_dict[0] = ['1645_54']
data_dict[0.2] = ['1647_19']
data_dict[0.4] = ['1648_45']
data_dict[0.6] = ['1650_12']
data_dict[0.8] = ['1651_40']
data_dict[1.0] = ['1653_09']




(times,nbarlist,nbarerrs) = fit_rabi_flops(file_loc,file_ext,data_dict,trap_freq,plot_flops,excitation_scaling,time_2pi,nbar,etas,delta)


pyplot.figure()

##rate,stderr = plot_heating_rate(timeswithramp,nbarlistwithramp,nbarerrswithramp,None)
##print "{0:.2f}".format(rate) + ' +- ' + "{0:.2f}".format(stderr) + ' n/ms'
rate,stderr = plot_heating_rate(times,nbarlist,nbarerrs,'0.631 MHz')
print "{0:.2f}".format(rate) + ' +- ' + "{0:.2f}".format(stderr) + ' n/ms for 1.027 MHz'
pyplot.legend()
pyplot.show()
