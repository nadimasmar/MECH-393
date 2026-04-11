from Shaft import *
from Bearing import *

diameter_out = {
    0: 20,
    15: 30,
    25: 50,
    30: 39,
    157: 20
}

output_shaft = Shaft(172, diameter_out)
output_shaft.add_keyseat(30)
output_shaft.add_keyseat(121)
output_shaft.add_stress_concentration(25, 5)
output_shaft.add_stress_concentration(30, 2)
output_shaft.add_stress_concentration(15, 3)
output_shaft.add_stress_concentration(157, 3)

shaft_torque = -856300
output_shaft.mass = 1.727
gear_1_mass = 7.66
gear_2_mass = 2 # arbitrary
gear_1_diameter = 224
gear_2_diameter = 100
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
output_shaft.plot_maximum_stress_diagrams(True)