from Shaft import *
from Bearing import *

# counterclockwise motion
diameter_inter = {
    0: 15,
    15 : 25,
    20: 36,
    54: 40,
    57: 36,
    107: 40,
    110: 37.5,
    171: 25,
    176: 20
}

inter_shaft = Shaft(191, diameter_inter)
inter_shaft.add_keyseat(40.5)
inter_shaft.add_keyseat(137)
inter_shaft.add_stress_concentration(15, 2)
inter_shaft.add_stress_concentration(20, 2)
inter_shaft.add_stress_concentration(54, 2)
inter_shaft.add_stress_concentration(57, 2)
inter_shaft.add_stress_concentration(107, 2)
inter_shaft.add_stress_concentration(110, 2)
inter_shaft.add_stress_concentration(171, 2)

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
print("safety factor is " + str(inter_shaft.get_min_safety_factor()))
print(inter_shaft.point_loads_y)
print(inter_shaft.point_loads_z)


bearing_1_y, bearing_2_y = inter_shaft.point_loads_y[0:2]
bearing_1_x, bearing_2_x = inter_shaft.point_loads_z[0:2]

bearing_1 = Bearing("ball", 90, 0, bearing_1_x[1], bearing_1_y[1], 10)
bearing_2 = Bearing("ball", 90, 0, bearing_2_x[1], bearing_2_y[1], 10)

print(bearing_1.F_r)
print(bearing_1_x)
print(bearing_1_y)
# bearing_1.minimum_basic_load() # Use 6302 due to geometric limitation on shaft diameter for safety
bearing_2.minimum_basic_load() # 6304 from force reqs: bore is sufficient; perhaps leave space if desired
