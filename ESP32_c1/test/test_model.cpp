/* Test code used to start and test classifier model */
#include "esp_camera.h"
#include <WiFi.h>
#include "esp_heap_caps.h"

/* TFLite-Micro */
#include "model_data.h"   // vehicle_classifier_int8_tflite array
#include "tensorflow/lite/micro/micro_mutable_op_resolver.h"
#include "tensorflow/lite/micro/micro_interpreter.h"
#include "tensorflow/lite/schema/schema_generated.h"
#include "tensorflow/lite/version.h"

#define CAMERA_MODEL_AI_THINKER
#include "camera_pins.h"

const char* ssid     = "xx";
const char* password = "xx";

/* TFLite area */
constexpr int kTensorArenaSize = 256 * 1024;     
uint8_t* tensor_arena          = nullptr;
tflite::MicroInterpreter* interpreter = nullptr;
TfLiteTensor* input  = nullptr;
TfLiteTensor* output = nullptr;

/* Model & image parameters */
const int   IMG_W   = 96;
const int   IMG_H   = 96;
const float THRESH  = 0.90f;                         // heavy vehicle threshold

void setup() {
  Serial.begin(115200);
  Serial.setDebugOutput(true);
  Serial.println();

  /* Cam setup */
  camera_config_t cam;
  cam.ledc_channel = LEDC_CHANNEL_0;
  cam.ledc_timer   = LEDC_TIMER_0;
  cam.pin_d0 = Y2_GPIO_NUM;  cam.pin_d1 = Y3_GPIO_NUM;
  cam.pin_d2 = Y4_GPIO_NUM;  cam.pin_d3 = Y5_GPIO_NUM;
  cam.pin_d4 = Y6_GPIO_NUM;  cam.pin_d5 = Y7_GPIO_NUM;
  cam.pin_d6 = Y8_GPIO_NUM;  cam.pin_d7 = Y9_GPIO_NUM;
  cam.pin_xclk = XCLK_GPIO_NUM; cam.pin_pclk = PCLK_GPIO_NUM;
  cam.pin_vsync = VSYNC_GPIO_NUM; cam.pin_href = HREF_GPIO_NUM;
  cam.pin_sccb_sda = SIOD_GPIO_NUM; cam.pin_sccb_scl = SIOC_GPIO_NUM;
  cam.pin_pwdn  = PWDN_GPIO_NUM; cam.pin_reset = RESET_GPIO_NUM;
  cam.xclk_freq_hz = 20000000;
  cam.frame_size   = FRAMESIZE_QQVGA;          // 160×120
  cam.pixel_format = PIXFORMAT_RGB565;
  cam.fb_location  = CAMERA_FB_IN_PSRAM;
  cam.jpeg_quality = 12;
  cam.fb_count     = 1;

  if (esp_camera_init(&cam) != ESP_OK) {
    Serial.println("Camera error");  return;
  }

  /* Wi-Fi connect */
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) { delay(500); Serial.print("."); }
  Serial.printf("\nWiFi connected – IP: %s\n", WiFi.localIP().toString().c_str());

  /* Tensor arena (PSRAM) */
  tensor_arena = (uint8_t*)heap_caps_malloc(kTensorArenaSize,
                  MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
  if (!tensor_arena) { Serial.println("Arena allocation failed"); return;}

  /* Model */
  const tflite::Model* model = tflite::GetModel(vehicle_classifier_int8_tflite);
  if (model->version() != TFLITE_SCHEMA_VERSION) {
    Serial.println("Model error"); return;
  }

  static tflite::MicroMutableOpResolver<10> resolver;
  resolver.AddQuantize();      resolver.AddDequantize();  // INT8 path
  resolver.AddDepthwiseConv2D();
  resolver.AddConv2D();
  resolver.AddAveragePool2D();
  resolver.AddFullyConnected();
  resolver.AddReshape();
  resolver.AddAdd();
  resolver.AddMean();
  resolver.AddLogistic();      // Sigmoid output

  static tflite::MicroInterpreter static_interp(model, resolver,
                     tensor_arena, kTensorArenaSize);
  interpreter = &static_interp;

  if (interpreter->AllocateTensors() != kTfLiteOk) {
    Serial.println("Tensor allocation failed"); return;
  }

  input  = interpreter->input(0);
  output = interpreter->output(0);

  Serial.printf("arena usage: %d / %d B\n",
                interpreter->arena_used_bytes(), kTensorArenaSize);
  Serial.printf("Free internal heap: %d  |  Free PSRAM: %d\n",
                heap_caps_get_free_size(MALLOC_CAP_INTERNAL),
                heap_caps_get_free_size(MALLOC_CAP_SPIRAM));
}

void classifyImage() {
  camera_fb_t* fb = esp_camera_fb_get();
  if (!fb) { Serial.println("Frame error"); return; }

  const float in_scale = input->params.scale;        // 0.00392
  const int   in_zp    = input->params.zero_point;   // 0
  uint8_t* in_buf = input->data.uint8;
  int idx = 0;

  /* 160×120 RGB565 → 96×96 RGB quantized (uint8) */
  for (int y = 0; y < IMG_H; ++y) {
    int oy = y * fb->height / IMG_H;
    for (int x = 0; x < IMG_W; ++x) {
      int ox = x * fb->width / IMG_W;
      int pos = (oy * fb->width + ox) * 2;
      if (pos + 1 >= fb->len) continue;

      uint16_t pix = (fb->buf[pos] << 8) | fb->buf[pos + 1];
      uint8_t r = ((pix >> 11) & 0x1F) << 3;
      uint8_t g = ((pix >>  5) & 0x3F) << 2;
      uint8_t b =  (pix        & 0x1F) << 3;

      /* quantization */
      in_buf[idx++] = (uint8_t)((r / 255.0f) / in_scale + in_zp);
      in_buf[idx++] = (uint8_t)((g / 255.0f) / in_scale + in_zp);
      in_buf[idx++] = (uint8_t)((b / 255.0f) / in_scale + in_zp);
    }
  }
  esp_camera_fb_return(fb);

  if (interpreter->Invoke() != kTfLiteOk) {
    Serial.println("Invoke error"); return;
  }

  /* De-quantize output */
  int8_t out_q   = output->data.uint8[0];
  float  prob    = (out_q - output->params.zero_point) * output->params.scale;

  if (prob >= THRESH)
    Serial.printf("🔴 Heavy vehicle (prob=%.3f)\n", prob);
  else
    Serial.printf("🟢 Passenger vehicle (prob=%.3f)\n", prob);
}

void loop() {
  classifyImage();
  delay(10'000);   // 10 s
}
