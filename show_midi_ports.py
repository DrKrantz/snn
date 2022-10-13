import mido as md

in_devices = md.get_input_names()
print("INPUTS:")
[print(device_name) for device_name in md.get_input_names()]


print("OUTPUTS:")
[print(device_name) for device_name in md.get_output_names()]
