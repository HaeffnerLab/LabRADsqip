from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit
import labrad
from treedict import TreeDict

class ramp_wait_back(pulse_sequence):
	required_parameters = [				('Ramp', 'step_duration'),
							('Ramp', 'initial_field'),
							('Ramp', 'final_field'),
							('Ramp', 'total_steps'),
							('Ramp', 'multipole'),
							('advanceDACs', 'pulse_length'),
							('advanceDACs', 'times'),
							('Heating', 'background_heating_time'),

						
	]
	
	def sequence( self ):
		
		#cxn=labrad.connect()
		#self.dac_server=cxn.dac_server

		#initial_field = self.parameters['Ramp.initial_field']
		#final_field = self.parameters['Ramp.final_field']
		#multipole = self.parameters['Ramp.multipole']
                #initial_field = initial_field['V/mm']
                #final_field = final_field['V/mm']
		#total_steps = int(self.parameters['Ramp.total_steps'])

		#self.dac_server.ramp_multipole(multipole, initial_field, final_field, total_steps)

		step_duration = self.parameters['Ramp.step_duration']
                total_steps = self.parameters['Ramp.total_steps']
		total_steps = int(self.parameters['Ramp.total_steps'])
                step_duration = step_duration['us']
		time_interval = step_duration #in us
		time_interval = time_interval * 10**-6
		self.parameters['advanceDACs.times'] = [i*time_interval for i in range(0,total_steps+1)]


		pl = self.parameters.advanceDACs.pulse_length
		times = self.parameters.advanceDACs.times
		wait = self.parameters.Heating.background_heating_time
		wait = wait['s']
		for t in times:
			self.addTTL('adv', self.start+WithUnit(t, 's'), pl)
		t1=times[-1]+wait+(25*10**-6)
		new_times=[x+t1 for x in times]
		for i in new_times:
			self.addTTL('adv', self.start+WithUnit(i, 's'), pl)
                duration = time_interval* float(total_steps)
		self.end=self.start+WithUnit(duration, 's')+WithUnit(self.parameters.Heating.background_heating_time['s'],'s')+ WithUnit(duration, 's')
		
		
