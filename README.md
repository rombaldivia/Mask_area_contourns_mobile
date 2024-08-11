Mask_area_contourns_mobile is an advanced system that integrates visual detection with robotic control via a joystick. It identifies and measures areas and contours in real-time using computer vision techniques. The system can be manually controlled through a joystick or operate in an automatic mode, adjusting the robot's movement based on visual data.

Features
Real-Time Area and Contour Detection: Identify and measure specific areas and contours from live video feed.
Manual and Automatic Control: Switch between controlling the robot manually using a joystick or allowing it to navigate automatically based on detected visual data.
Flexible Configuration: Easily adjust detection parameters (HSV values) through sliders in the GUI.
Usage
Running the Full System
To run the full system with both visual detection and joystick control, execute:
python main.py
This will launch the GUI, allowing you to adjust HSV values, view the live video feed, and control the robot using the joystick.
Testing the Joystick Module
If you want to test the joystick module separately to ensure it works correctly:
python joystick_robotic.py
This will launch a simple window where you can test the joystick's functionality without the visual detection components.
