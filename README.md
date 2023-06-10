This is a software repo for interfacing with the 2 meter telescope used in my PhD research. 
The folder telescope_control consists of a GUI which handles sending servo controls to the azimuth and elevation motors, monitering housekeeping data to insure 
data is being taken under optimal conditions, and data acquisition. There are also a number of files for post-analysis such as realtime_gp 
and the notebooks used for a variety of analysis tasks in the notebooks folder.

Basic Layout of the user interface. Bottom left allows for system monitering of various parameters of interest, as well as buttons to 
save your current interface configuration, turn the motor on/off, stop motion or exit GUI, and begin acquiring science data (acq_tel) 
which is then saved to H5 file on an onboard computer. 

<img width="494" alt="Screen Shot 2023-06-05 at 3 33 31 PM" src="https://github.com/arikaplan/polaris_software/assets/8053891/e4944b87-d792-4b4d-8b55-311ec1783ded">

The top left shows basic telescope motion commands, giving the option to either move to a specified location, or by a specified amount. 
the radec/azel button toggles between these commands being input in either horizontal or celestial coordinates. 

The right side of the interface gives the option for live plotting of data for a science channels as well cryogenic temperature sensors. 
The top plot is a live feed of data binned to azimuth and elevation, and the bottom plot is a time stream

Other tabs include the functionality to perform different scan types such as a helical scan, constant elevation scan, and tracking of points
on the sky or celestial objects by either tracing a box around the object or linearly scanning back and forth across the centroid

<img width="494" alt="Screen Shot 2023-06-05 at 3 33 46 PM" src="https://github.com/arikaplan/polaris_software/assets/8053891/cb46744c-f2a7-4c10-bda7-890e3f300d94">
<img width="494" alt="Screen Shot 2023-06-05 at 3 33 50 PM" src="https://github.com/arikaplan/polaris_software/assets/8053891/42581e86-cd63-4065-916c-d1bb7b5b7c37">
<img width="494" alt="Screen Shot 2023-06-05 at 3 33 53 PM" src="https://github.com/arikaplan/polaris_software/assets/8053891/a337ea39-d381-4409-b1a0-24a134c1a5b4">
<img width="494" alt="Screen Shot 2023-06-05 at 3 33 58 PM" src="https://github.com/arikaplan/polaris_software/assets/8053891/7ca001f5-1699-4ebe-8a23-5547fcd5f0f5">
<img width="494" alt="Screen Shot 2023-06-05 at 3 34 01 PM" src="https://github.com/arikaplan/polaris_software/assets/8053891/3ceba6ab-8bba-4075-a482-d0a4e7816d67">

The last tab enables setting configuration parameters for the telescope motion such as speed and acceleration, as well as calibrating 
pointing offsets.

<img width="494" alt="Screen Shot 2023-06-05 at 3 34 06 PM" src="https://github.com/arikaplan/polaris_software/assets/8053891/2a9e8c02-a508-4c71-bfa1-090ced125586">


## Results from selected analysis notebooks:

Atmospheric emmission modeled with ATMOS32 and plotted against foreground spectral behavior with data simulated using PySM3 for the planck sky model ([notebook/atmospheric plot.ipynb](https://github.com/arikaplan/polaris_software/blob/master/notebook/atmospheric%20plot.ipynb))
![atmospheric_plot](https://github.com/arikaplan/polaris_software/assets/8053891/342b4f4d-1ea7-4c4f-855f-4189463d073d)


Sky dip method used for calibrating instrument using elevation dependent atmospheric emission:
([notebook/Sky_dip.ipynb](https://github.com/arikaplan/polaris_software/blob/master/notebook/Sky_dip.ipynb))
<img width="626" alt="image" src="https://github.com/arikaplan/polaris_software/assets/8053891/04aa32f5-6cce-4fad-89b7-b573114f97b6">

Measuring the rise and fall of crab nebula through our rotating beam, then binning to celestial coordinates to measure offsets in our pointing calibration ([notebook/pointing_cal.ipynb](https://github.com/arikaplan/polaris_software/blob/master/notebook/pointing_cal.ipynb))

<img width="503" alt="image" src="https://github.com/arikaplan/polaris_software/assets/8053891/96ad8529-9ca2-443a-9a56-b62882f3d9e4">
<img width="550" alt="image" src="https://github.com/arikaplan/polaris_software/assets/8053891/477a8b75-1d67-4b84-b6dd-883d796b1f1d">

Mapping polarized galactic foregrounds after passing raw data through analysis pipeline(demodulation into polarization states, data structuring, data cleaning, destriping low frequency correlated noise) as well as producing angular power spectrum for maps. Due to low integration time these maps were consistent with a white noise power spectrum ([notebook/mapmaking.ipynb](https://github.com/arikaplan/polaris_software/blob/master/notebook/mapmaking.ipynb))

<img width="579" alt="image" src="https://github.com/arikaplan/polaris_software/assets/8053891/bd4c30f9-8c35-4bc8-807c-3383d1c184e8">
<img width="579" alt="image" src="https://github.com/arikaplan/polaris_software/assets/8053891/276b1eda-0ef2-43e3-b2fa-a70ef728da0a">
<img width="579" alt="image" src="https://github.com/arikaplan/polaris_software/assets/8053891/df2dc5a5-0053-4ce1-8be3-71c8a84845fe">
<img width="579" alt="image" src="https://github.com/arikaplan/polaris_software/assets/8053891/1b75c3a7-c312-4db7-9c44-76f1a827d7ba">

<img width="1226" alt="image" src="https://github.com/arikaplan/polaris_software/assets/8053891/301c5c8c-9fc1-42be-a7bb-0899a1e646ab">
<img width="1226" alt="image" src="https://github.com/arikaplan/polaris_software/assets/8053891/0293f57e-9fdb-4da0-8738-94a3eff47a2e">
<img width="1226" alt="image" src="https://github.com/arikaplan/polaris_software/assets/8053891/f1b7a22c-ae5f-4a8e-b026-09a3623b5f06">



