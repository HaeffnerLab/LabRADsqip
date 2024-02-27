import labrad
from labrad.units import WithUnit
import numpy as np
from matplotlib import pyplot

identify_exposure = WithUnit(0.5, 's')
start_x = 300; stop_x = 400
start_y = 235; stop_y = 250
image_region = (1,1,start_x,stop_x,start_y,stop_y)

pixels_x = (stop_x - start_x + 1) 
pixels_y = (stop_y - start_y + 1)

cxn = labrad.connect()
cam = cxn.andor_server




cam.abort_acquisition()
initial_exposure = cam.get_exposure_time()
cam.set_exposure_time(identify_exposure)
initial_region = cam.get_image_region()
cam.set_image_region(*image_region)
cam.set_acquisition_mode('Single Scan')
cam.start_acquisition()
cam.wait_for_acquisition()
image = cam.get_acquired_data().asarray
np.save('sample', image)


image = np.reshape(image, (pixels_y, pixels_x))

pyplot.contour(image)


cam.set_exposure_time(initial_exposure)
cam.set_image_region(initial_region)
cam.start_live_display()


pyplot.show()