from Shaft import *
from Bearing import *

# counterclockwise motion
diameter_inter = {
    0: 15,
    13 : 25,
    18: 36,
    22.85: 34,
    25: 36,
    52: 44,
    55: 36,
    105: 44,
    108: 38,
    162: 34,
    164.15: 36,
    169.9: 25
}

inter_shaft = Shaft(186.9, diameter_inter)
inter_shaft.add_keyseat(46)
inter_shaft.add_keyseat(136)
inter_shaft.add_stress_concentration(13, 1)
inter_shaft.add_stress_concentration(169.9, 1)
inter_shaft.add_stress_concentration(22.85, 0.15)
inter_shaft.add_stress_concentration(25, 0.15)
inter_shaft.add_stress_concentration(162, 0.15)
inter_shaft.add_stress_concentration(164.15, 0.15)
inter_shaft.add_stress_concentration(18, 2)
inter_shaft.add_stress_concentration(52, 2)
inter_shaft.add_stress_concentration(55, 2)
inter_shaft.add_stress_concentration(105, 2)
inter_shaft.add_stress_concentration(108, 2)

shaft_torque = 367000
inter_shaft.mass = 1.335
gear_1_mass = 3.442
gear_2_mass = 2.542
gear_1_diameter = 168
gear_2_diameter = 96
gear_1_pos = 46
gear_2_pos = 136
inter_shaft.torque = (gear_1_pos, gear_2_pos, shaft_torque)
bearing_1_pos = 6.5
bearing_2_pos = 178.4

inter_shaft.point_load_balance(bearing_1_pos,
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

print("fatigue safety factor is " + str(inter_shaft.get_min_safety_factor()))
Ns = inter_shaft.get_static_safety_factor()
print("static safety factor is " + str(Ns))