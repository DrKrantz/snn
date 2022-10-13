import mido as md


inputs_names = {}.fromkeys(md.get_input_names())
print("INPUTS:")
[print('  "{}"'.format(device_name)) for device_name in inputs_names]

output_names = {}.fromkeys(md.get_output_names())

print("OUTPUTS:")
[print('  "{}"'.format(device_name)) for device_name in output_names]
