from common.okfpgaservers.pulser.pulse_sequences.plot_sequence import SequencePlotter as plot
from spectrum_rabi_with_multipole_ramp import spectrum_rabi_with_multipole_ramp
import numpy as np
from treedict import TreeDict
plt=plot(spectrum_rabi_with_multipole_ramp,'123','abc')
print plt.extractInfo()

