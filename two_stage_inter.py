from Shaft import *
import matplotlib as mpl

'''
cmap = mpl.colormaps.get_cmap("YlGnBu")
mpl.rcParams['cmap'] = cmap'''

# counterclockwise motion
diameter_inter = {
    0: 20,
    20: 30,
    25: 26,
    27: 30,
    54: 40,
    57: 30,
    107: 40,
    110: 30,
    164: 26,
    166: 30,
    171: 20
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

print(inter_shaft.point_loads_y)
print(inter_shaft.torque)
print(inter_shaft.get_min_safety_factor())
print(inter_shaft.min_diameter(inter_shaft.torque[2], 230, 0))

defl = inter_shaft.get_deflection_at(73)
print(inter_shaft.get_torsion_angle_at(124))