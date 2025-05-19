#ifndef MODEL_DATA_H_
#define MODEL_DATA_H_

extern const unsigned char vehicle_classifier_int8_tflite[];
extern const unsigned int vehicle_classifier_int8_tflite_len;

#endif  // MODEL_DATA_H_

// model_data.cpp could not be committed to Git because of size.
// To use this file:
// 1. Run the Python script cpp_array.py to generate the model data
// 2. Rename the generated file to model_data.cpp
// 3. Add this line at the top of model_data.cpp:  #include "model_data.h"
// 4. Place model_data.cpp in the same folder as your main ESP32 project.
