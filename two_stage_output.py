from Shaft import *
from Bearing import *

diameter_out = {
    0: 20,
    15: 30,
    25: 50,
    30: 40, # changed this for the bearing, you could make a small lip for it if you want
    157: 20
}

output_shaft = Shaft(172, diameter_out)
output_shaft.add_keyseat(30)
output_shaft.add_keyseat(121)
output_shaft.add_stress_concentration(15, 3)
output_shaft.add_stress_concentration(25, 5)
output_shaft.add_stress_concentration(30, 2)
output_shaft.add_stress_concentration(157, 3)

shaft_torque = -856300
output_shaft.mass = 1.727
gear_1_mass = 7.66
gear_2_mass = 8 # arbitrary
gear_1_diameter = 224
gear_2_diameter = 128
gear_1_pos = 30
gear_2_pos = 121
output_shaft.torque = (gear_1_pos, gear_2_pos, shaft_torque)
bearing_1_pos = 0
bearing_2_pos = 135

output_shaft.point_load_balance(bearing_1_pos,
                               bearing_2_pos,
                               gear_1_pos,
                               gear_2_pos,
                               gear_1_mass,
                               gear_2_mass,
                               gear_1_diameter,
                               gear_2_diameter,
                               20,
                               shaft_torque,
                               shaft_torque)

print("safety factor is " + str(output_shaft.get_min_safety_factor()))

bearing_1_y, bearing_2_y = output_shaft.point_loads_y[0:2]
bearing_1_x, bearing_2_x = output_shaft.point_loads_z[0:2]

bearing_1 = Bearing("ball", 90, 0, bearing_1_x[1], bearing_1_y[1], 10)
bearing_2 = Bearing("ball", 90, 0, bearing_2_x[1], bearing_2_y[1], 10)

print(bearing_1.F_r)
print(bearing_2.F_r)
# bearing_1.minimum_basic_load() # 6304 by load requirement: bore is met
# bearing_2.minimum_basic_load() # 6308 by shaft requirement

print(bearing_1.get_LD_bearing(13350))
print(bearing_1.get_LD_bearing(32708))