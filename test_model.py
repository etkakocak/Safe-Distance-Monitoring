# test_model.py
import os, cv2, numpy as np, tensorflow as tf

# TFLite model
interpreter = tf.lite.Interpreter("vehicle_classifier_int8.tflite")
interpreter.allocate_tensors()

in_det  = interpreter.get_input_details()[0]
out_det = interpreter.get_output_details()[0]

in_scale,  in_zp  = in_det['quantization']       # scale and zero_point
out_scale, out_zp = out_det['quantization']

IMG_SIZE  = (96, 96)     
THRESHOLD = 0.90         # threshold for heavy vehicle
TEST_DIR  = "dataset/valid"

print(f"Input dtype : {in_det['dtype']},  scale={in_scale}, zp={in_zp}")
print(f"Output dtype: {out_det['dtype']}, scale={out_scale}, zp={out_zp}\n")

for name in sorted(os.listdir(TEST_DIR)):
    path = os.path.join(TEST_DIR, name)
    img  = cv2.imread(path)
    if img is None:
        print(f"Skip {name}")
        continue

    # pre processing
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, IMG_SIZE, interpolation=cv2.INTER_AREA)
    img = img.astype(np.float32)                        
    img = np.expand_dims(img, 0)                        # (1,96,96,3)

    # input quantization
    img_q = np.uint8(img / in_scale + in_zp)
    interpreter.set_tensor(in_det['index'], img_q)
    interpreter.invoke()

    # output de-quantization
    out_q = interpreter.get_tensor(out_det['index']).squeeze()          # uint8 
    prob  = float((out_q - out_zp) * out_scale)                         

    label = "Heavy (1)" if prob >= THRESHOLD else "Car (0)"
    print(f"{name:25s}  prob={prob:.3f}  →  {label}")
