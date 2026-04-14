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
output_shaft.mass = 2.049
gear_1_mass = 7.649
gear_2_mass = 8 # arbitrary
gear_1_diameter = 224
gear_2_diameter = 200
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

print("fatigue safety factor is " + str(output_shaft.get_min_safety_factor()))
Ns = output_shaft.get_static_safety_factor()
print("static safety factor is " + str(Ns))