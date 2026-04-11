from Shaft import *
from Bearing import *

# counterclockwise motion
diameter_inter = {
    0: 30,
    20: 41,
    25: 39,
    27: 41,
    54: 45,
    57: 41,
    107: 45,
    110: 41,
    164: 39,
    166: 41,
    171: 30
}

inter_shaft = Shaft(191, diameter_inter)
inter_shaft.add_keyseat(40.5)
inter_shaft.add_keyseat(137)
inter_shaft.add_stress_concentration(20, 2)
inter_shaft.add_stress_concentration(54, 2)
inter_shaft.add_stress_concentration(57, 2)
inter_shaft.add_stress_concentration(107, 2)
inter_shaft.add_stress_concentration(110, 2)
inter_shaft.add_stress_concentration(171, 2)

inter_shaft.add_stress_concentration(25, 0.5)
inter_shaft.add_stress_concentration(27, 0.5)
inter_shaft.add_stress_concentration(164, 0.5)
inter_shaft.add_stress_concentration(166, 0.5)

shaft_torque = 367000
inter_shaft.mass = 0.944
gear_1_mass = 3.457
gear_2_mass = 2.706
gear_1_diameter = 168
gear_2_diameter = 96
gear_1_pos = 40.5
gear_2_pos = 137
inter_shaft.torque = (gear_1_pos, gear_2_pos, shaft_torque)
bearing_1_pos = 0
bearing_2_pos = 191

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


print(inter_shaft.torque)
print(inter_shaft.get_min_safety_factor())
print(inter_shaft.min_diameter(inter_shaft.torque[2], 230, 0))

defl = inter_shaft.get_deflection_at(73)
print(inter_shaft.get_torsion_angle_at(124))
'''inter_shaft.plot_shear_bending_diagrams("y")
inter_shaft.plot_deflection_diagrams("y")'''

bearing_1_y, bearing_2_y = inter_shaft.point_loads_y[0:2]
bearing_1_x, bearing_2_x = inter_shaft.point_loads_z[0:2]

bearing_1 = Bearing("ball", 90, 0, bearing_1_x[1], bearing_1_y[1], 10)
bearing_2 = Bearing("ball", 90, 0, bearing_2_x[1], bearing_2_y[1], 10)

print(bearing_1.F_r)
print(bearing_1_x)
print(bearing_1_y)
bearing_1.minimum_basic_load()
bearing_2.minimum_basic_load()
