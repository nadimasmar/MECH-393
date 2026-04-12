from Shaft import *
from Bearing import *

# This code is assuming that the input shaft is turning
# clockwise. This would make the point load from the gear
# torquing downward on the gear. 

diameter_input = {
    0 : 30,
    144 : 35,
    147 : 30,
    157 : 17
}

# While the bearing on the inside of the casing is 14 mm wide, I left 1 mm for spacing purposes
# to prevent grinding on any walls.

input_shaft = Shaft(167, diameter_input)
input_shaft.add_keyseat(123)
input_shaft.add_keyseat(35)
input_shaft.add_stress_concentration(144, 2)
input_shaft.add_stress_concentration(147, 2)
input_shaft.add_stress_concentration(157, 1)

print(input_shaft.mass)
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
                               2 * input_gear_mass,
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
'''input_shaft.plot_maximum_stress_diagrams(True)'''

bearing_1_y, bearing_2_y = input_shaft.point_loads_y[0:2]
bearing_1_x, bearing_2_x = input_shaft.point_loads_z[0:2]

bearing_1 = Bearing("ball", 90, 0, bearing_1_x[1], bearing_1_y[1], 10)
bearing_2 = Bearing("ball", 90, 0, bearing_2_x[1], bearing_2_y[1], 10)

print(bearing_1.F_r)
print(bearing_1_x)
print(bearing_1_y)
print(bearing_1.C) # 6306 by shaft size
print(bearing_2.C) # 6303 by force measurement ==> reduce diameter to 17 mm

print(bearing_1.get_LD_bearing(16910))
print(bearing_2.get_LD_bearing(10324))