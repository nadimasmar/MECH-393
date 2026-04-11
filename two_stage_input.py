from Shaft import *
from Bearing import *

# This code is assuming that the input shaft is turning
# clockwise. This would make the point load from the gear
# torquing downward on the gear. 

diameter_input = {
    0 : 15, 
    10 : 30,
    144 : 32,
    147 : 30,
    157 : 15
}

input_shaft = Shaft(167, diameter_input)
input_shaft.add_keyseat(123)
input_shaft.add_keyseat(35)
input_shaft.add_stress_concentration(144, 2)
input_shaft.add_stress_concentration(147, 2)

input_shaft.mass = 0.41561
unmounted_gear_pos = 35
input_gear_pos = 123
input_gear_mass = 1.208
input_gear_pitch_d = 72
input_torque = -157283
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

input_shaft.torque = (unmounted_gear_pos, input_gear_pos, input_torque)
#input_shaft.plot_maximum_stress_diagrams(True)
print(input_shaft.point_loads_y)
print(input_shaft.point_loads_z)

Nf = input_shaft.get_min_safety_factor()
print("safety factor is " + str(Nf))