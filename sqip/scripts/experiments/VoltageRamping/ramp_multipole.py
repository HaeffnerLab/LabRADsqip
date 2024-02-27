from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from sqip.scripts.PulseSequences.resetDACs import reset_DACs
from sqip.scripts.PulseSequences.ramp_wait_back_sequence import ramp_wait_back
from sqip.scripts.PulseSequences.spectrum_rabi_with_multipole_ramp import spectrum_rabi_with_multipole_ramp
from common.abstractdevices.script_scanner.scan_methods import experiment
from sqip.scripts.experiments.Experiments729.excitations import excitation_729_with_multipole_ramp
#from sqip.scripts.scriptLibrary.common_methods_729 import common_methods_729 as cm
#from sqip.scripts.scriptLibrary import dvParameters
#from sqip.scripts.experiments.Crystallization.crystallization import crystallization
#import time
#from numpy import linspace

class ramp_multipole(experiment):
	name = 'ramp_multipole'
	required_parameters = [
							('Ramp', 'duration'),
							('Ramp', 'initial_field'),
							('Ramp', 'final_field'),
							('Ramp', 'total_steps'),
							('Ramp', 'multipole'),

							('advanceDACs', 'times'),
							('advanceDACs', 'pulse_length'),

							('Heating', 'background_heating_time'),
							#('OpticalPumping','optical_pumping_enable'), 
                           				#('SidebandCooling','sideband_cooling_enable'),
							#('DopplerCooling','doppler_cooling_duration'),
						  ]

####	
	@classmethod
	def all_required_parameters(cls):
		parameters = set(cls.required_parameters)
		parameters = parameters.union(set(excitation_729_with_multipole_ramp.all_required_parameters()))
		parameters = list(parameters)
		#removing parameters we'll be overwriting, and they do not need to be loaded
#		parameters.remove(('Excitation_729','rabi_excitation_amplitude'))
#		parameters.remove(('Excitation_729','rabi_excitation_duration'))
#		parameters.remove(('Excitation_729','rabi_excitation_frequency'))
		return parameters	
###	
	def initialize(self, cxn, context, ident):
		self.ident = ident  #
		self.dac_server = cxn.dac_server
		self.pulser = cxn.pulser
	#	self.pulser.switch_manual('rst',True)
		# self.startPosition = self.dac_server.get_position()

	def run(self, cxn, context):
                #print self.paramters['Ramp.duration']['us']
		initial_field = self.parameters['Ramp.initial_field']
		final_field = self.parameters['Ramp.final_field']
		multipole = self.parameters['Ramp.multipole']
                initial_field = initial_field['V/mm']
                final_field = final_field['V/mm']
		total_steps = int(self.parameters['Ramp.total_steps'])

		self.dac_server.ramp_multipole(multipole, initial_field, final_field, total_steps)
                
		#duration = self.parameters['Ramp.duration']
                #total_steps = self.parameters['Ramp.total_steps']
		#total_steps = int(self.parameters['Ramp.total_steps'])
                #duration = duration['us']		
		#time_interval = duration/float(total_steps) #in us
		#time_interval = time_interval * 10**-6
		#self.parameters['advanceDACs.times'] = [i*time_interval for i in range(0,total_steps+1)]	

		#duration = float(self.parameters['Ramp.duration'])
##		initial_field = float(self.parameters['Ramp.initial_field'])
##		final_field = float(self.parameters['Ramp.final_field'])
##		multipole = str(self.parameters['Ramp.multipole'])
		# shuttle_times = self.dac_server.shuttle(endPosition, step_size, duration, loop, overshoot)
		# shuttle_times = self.dac_server.get_shuttle_times()
                #total_steps =
		
		#duration = self.parameters['Ramp.duration']
                #total_steps = self.parameters['Ramp.total_steps']
		#total_steps = int(self.parameters['Ramp.total_steps'])
                #duration = duration['us']		
		#time_interval = duration/float(total_steps) #in us
		#time_interval = time_interval * 10**-6
		#self.parameters['advanceDACs.times'] = [i*time_interval for i in range(0,total_steps+1)]
		
		self.seq = spectrum_rabi_with_multipole_ramp(self.parameters)
 	       	self.doSequence()


		#self.seq = spectrum_rabi_with_multipole_ramp(self.parameters)
 	        #self.doSequence()
		
		#self.seq = reset_DACs(self.parameters)
		#self.doSequence()


	def finalize(self, cxn, context):
		pass

	def doSequence(self):
		self.seq.programSequence(self.pulser)
		self.pulser.start_single()
		self.pulser.wait_sequence_done()
		self.pulser.stop_sequence()

if __name__ == '__main__':
	import labrad
	cxn = labrad.connect()
	scanner = cxn.scriptscanner
	exprt = ramp_multipole(cxn=cxn)
	ident = scanner.register_external_launch(exprt.name)
	exprt.execute(ident)
