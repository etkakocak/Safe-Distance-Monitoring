# Safe Distance Monitoring
This project presents a prototype system designed to monitor the following distances between vehicles and detect tailgating violations in real time. Built with embedded microcontrollers and integrated sensor technology, the system aims to demonstrate the feasibility of distance monitoring enforcement. By combining real-time data processing, signal processing, machine learning-based vehicle classification, and adaptive safety thresholds, the prototype provides an autonomous lab-scale proof of concept.  

This project was conducted as part of a Bachelor's thesis in Computer Science.

## Folder Structure
``/RPI_c1``: Contains the MicroPython scripts for the main embedded board (Raspberry Pi Pico W) in Circuit 1, which serves as the prototype of the Safe Distance Monitoring Device.  
``/ESP32_c1``: Contains the Embedded C/C++ scripts for the ESP32-CAM board in Circuit 1, responsible for running the vehicle classification model using computer vision.  
``/RPI_c2``: Contains the MicroPython scripts for the Raspberry Pi Pico W in Circuit 2, which simulates a representative prototype of existing speed camera units with radar functionality.