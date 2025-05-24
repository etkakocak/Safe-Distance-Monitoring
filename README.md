# Safe Distance Monitoring
This project presents a prototype system designed to monitor the following distances between vehicles and detect tailgating violations in real time. Built with embedded microcontrollers and integrated sensor technology, the system aims to demonstrate the feasibility of distance monitoring enforcement. By combining real-time data processing, signal processing, machine learning-based vehicle classification, and adaptive safety thresholds, the prototype provides an autonomous lab-scale proof of concept.  

*This project was conducted as part of a Bachelor's thesis in Computer Science.*

## Folder Structure
``/RPI_c1``: Contains the MicroPython scripts for the main embedded board (Raspberry Pi Pico W) in Circuit 1, which serves as the prototype of the Safe Distance Monitoring Device.  
``/ESP32_c1``: Contains the Embedded C/C++ scripts for the ESP32-CAM board in Circuit 1, responsible for running the vehicle classification model using computer vision.  
``/RPI_c2``: Contains the MicroPython scripts for the Raspberry Pi Pico W in Circuit 2, which simulates a representative prototype of existing speed camera units with radar functionality.

## Architecture
The system architecture is composed of two interconnected circuits: the safe distance monitoring device (circuit 1) classifies vehicle types using an onboard ML model, adapts to real-time weather conditions, calculates a safe distance threshold, and detects whether the following distance is safe. The speed camera unit simulator device (circuit 2) mimics radar-based speed measurement and communicates with the main device to simulate a full enforcement system.  

**Hardware**: Raspberry Pi Pico W, ESP32-CAM, DS18B20 (temperature sensor), and HC-SR04 (ultrasonic sensor).  
**Software**: Python (training and preparing the ML vehicle classification model), MicroPython (programming Raspberry Pi Pico W), and Embedded C/C++ (programming ESP32-CAM via ESP-IDF).  
**Machine Learning**: TensorFlow with MobileNetV2 backbone, quantized and deployed as a TFLite model.  
**External API**: OpenWeatherMap for real-time weather data.  
**Communication**: UART and GPIO are used for inter-device communication between subsystems.