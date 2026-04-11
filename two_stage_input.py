from Shaft import *

# This code is assuming that the input shaft is turning
# clockwise. This would make the point load from the gear
# torquing downward on the gear. 

diameter_input = {
    0: 20,
    15: 30,
    100 : 26,
    102 : 30,
    144: 40,
    147: 30,
    152: 20
}

input_shaft = Shaft(167, diameter_input)
input_shaft.add_keyseat(123)
input_shaft.add_keyseat(35)
input_shaft.add_stress_concentration(100, 0.5)
input_shaft.add_stress_concentration(102, 0.5)
input_shaft.add_stress_concentration(144, 2)
input_shaft.add_stress_concentration(147, 2)

input_shaft.mass = 0.41561
unmounted_gear_pos = 35
input_gear_pos = 123
input_gear_mass = 1.208
input_gear_pitch_d = 72
input_torque = 157283
bearing_2_pos = 158
bearing_1_pos = 84

input_shaft.point_load_balance(bearing_1_pos,
                               bearing_2_pos,
                               unmounted_gear_pos,
                               input_gear_pos,
                               input_gear_mass,
                               input_gear_mass,
                               input_gear_pitch_d,
                               128,
                               20,
                               input_torque,
                               input_torque,
                               )

print(input_shaft.point_loads_y)
print(input_shaft.point_loads_z)

input_shaft.torque = (unmounted_gear_pos, input_gear_pos, input_torque)
Nf = input_shaft.get_min_safety_factor()
print(Nf)
d = input_shaft.min_diameter(input_shaft.torque[2],265,0)
print(d)