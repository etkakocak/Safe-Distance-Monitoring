# This file is only valid for VSCode + ESP-IDF environment.
# If you are using Arduino IDE you do not need this file.

idf_component_register(
    SRCS "main.cpp" "model_data.cpp"
    INCLUDE_DIRS "."
    REQUIRES
        esp32-camera
        esp_timer
        esp_http_server
        nvs_flash
        esp_wifi
        esp_event
        log
)