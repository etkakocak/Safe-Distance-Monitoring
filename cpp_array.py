def to_cpp_array(filename, varname="model"):
    with open(filename, "rb") as f:
        data = f.read()

    hex_array = ', '.join(f'0x{b:02x}' for b in data)
    lines = []
    lines.append(f'const unsigned char {varname}[] = {{')
    for i in range(0, len(data), 12):
        chunk = ', '.join(f'0x{b:02x}' for b in data[i:i+12])
        lines.append(f'  {chunk},')
    lines.append('};\n')
    lines.append(f'const unsigned int {varname}_len = {len(data)};')
    
    return '\n'.join(lines)


with open("model_data.cc", "w") as f:
    f.write(to_cpp_array("vehicle_classifier_int8.tflite", "vehicle_classifier_int8_tflite"))

print("Done.")