from Shaft import *

# This code is assuming that the input shaft is turning
# clockwise. This would make the point load from the gear
# torquing downward on the gear. 

diameter_input = {
    0: 20,
    100 : 16,
    102 : 20,
    144: 30,
    147: 20,
}

input_shaft = Shaft(167, diameter_input)
input_shaft.add_keyseat(123)
input_shaft.add_keyseat(35)
input_shaft.add_stress_concentration(100, 0.5)
input_shaft.add_stress_concentration(102, 0.5)
input_shaft.add_stress_concentration(144, 2)
input_shaft.add_stress_concentration(147, 2)

print(input_shaft.stress_factors)

input_shaft.mass = 0.41561
unmounted_gear_pos = 35
input_gear_pos = 123
input_gear_mass = 1.20788
input_gear_pitch_d = 72
input_torque = 157283
bearing_in_pos = 158
bearing_out_pos = 84

input_shaft.point_load_balance(bearing_in_pos,
                               bearing_out_pos,
                               unmounted_gear_pos,
                               input_gear_pos,
                               input_gear_mass,
                               input_gear_mass,
                               input_gear_pitch_d,
                               input_gear_pitch_d,
                               20,
                               input_torque,
                               input_torque,
                               )

print(input_shaft.point_loads_y)
print(input_shaft.point_loads_z)
print(input_shaft.distributed_loads_y)

input_shaft.torque = input_torque
Nf = input_shaft.get_min_safety_factor()
print(Nf)

input_shaft.plot_stress_diagrams()