from Shaft import *

diameter_out = {
    0: 30,
    25: 40,
    125: 36,
    127: 40,
    167: 50,
    172: 30
}

output_shaft = Shaft(197, diameter_out)
output_shaft.add_keyseat(55)
output_shaft.add_keyseat(146)
output_shaft.add_stress_concentration(125, 0.5)
output_shaft.add_stress_concentration(127, 0.5)
output_shaft.add_stress_concentration(25, 2)
output_shaft.add_stress_concentration(167, 2)
output_shaft.add_stress_concentration(172, 2)

shaft_torque = 856300
output_shaft.mass = 1.727
gear_1_mass = 7.66
gear_2_mass = 2 # arbitrary
gear_1_diameter = 224
gear_2_diameter = 48
gear_1_pos = 55
gear_2_pos = 146
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


print(output_shaft.point_loads_y)
print(output_shaft.get_min_safety_factor())