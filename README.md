# ModelLINK
Spatial Augmented Reality System to Aid Prototyping of Piston-Based Linkage Mechanisms

#Requirements
You will need:
- A webcam 
- A worktop 
- Aruco Markers - https://fodi.github.io/arucosheetgen/ (Dictionary: 4x4)
- A projector (one that projects nothing for black)
- A monitor to display the graphs

#Installation
1. Check that you have python 3 in terminal/command prompt
```
python3 --version 
```
2. Install OpenCV
```
pip3 install opencv-contrib-python
```
and 
```
pip3 install opencv-python
```

3. Download the Unity executable - File Name:

build the thing and make an exe file 

#Set Up
1. Use Aruco Markers 1-4 as calibration markers (i.e one in each corner of the projected surface) 
2. Measure the dimensions of the projected surface and change line 67 in aruco.py from:
       width,height = 950,590
   to match your dimensions (in mm)
3. Label the rest of your aruco markers as follows:
      | Aruco Number  | Label |
      | ------------- | ------------- |
      | 5  | Ground  |
      | 6  | Link 1 End  |
      | 6  | Piston 1 End  |



