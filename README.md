This is a software repo for interfacing with the 2 meter telescope used in my PhD research. 
The folder telescope_control consists of a GUI which handles sending servo controls to the azimuth and elevation motors, monitering housekeeping data to insure 
data is being taken under optimal conditions, and data acquisition. There are also a number of files for post-analysis such as realtime_gp 
and the notebooks used for a variety of tasks in the notebooks folder.

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
