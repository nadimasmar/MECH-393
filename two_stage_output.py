from Shaft import *
from Bearing import *

diameter_out = {
    0: 25,
    17: 40,
    33: 50,
    38: 45,
}

output_shaft = Shaft(180, diameter_out)
output_shaft.add_keyseat(59)
output_shaft.add_keyseat(150)
output_shaft.add_stress_concentration(38, 2)
output_shaft.add_stress_concentration(33, 2)
output_shaft.add_stress_concentration(17, 1)

shaft_torque = -856300
output_shaft.mass = 1.677
gear_1_mass = 7.649
gear_2_mass = 8 # arbitrary
gear_1_diameter = 224
gear_2_diameter = 224
gear_1_pos = 59
gear_2_pos = 150
output_shaft.torque = (gear_1_pos, gear_2_pos, shaft_torque)
bearing_1_pos = 8.5
bearing_2_pos = 102.5

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
Ns = output_shaft.get_static_safety_factor()
print("static safety factor is " + str(Ns))
output_shaft.plot_maximum_stress_diagrams(True)

bearing_1_y, bearing_2_y = output_shaft.point_loads_y[0:2]
bearing_1_x, bearing_2_x = output_shaft.point_loads_z[0:2]

bearing_1 = Bearing("ball", 90, 0, bearing_1_x[1], bearing_1_y[1], 10)
bearing_2 = Bearing("ball", 90, 0, bearing_2_x[1], bearing_2_y[1], 10)

print(bearing_1.F_r)
print(bearing_2.F_r)
# bearing_1.minimum_basic_load() # 6305 by load requirement: bore is met
# bearing_2.minimum_basic_load() # 6308 by shaft requirement

print(bearing_1.get_LD_bearing(16910))
print(bearing_1.get_LD_bearing(32708))