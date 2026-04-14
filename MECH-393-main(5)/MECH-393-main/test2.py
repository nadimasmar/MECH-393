from Shaft import *

# create a shaft

test = Shaft(500,15)
print(test.length)
print(test.diameter)
print(test.distributed_loads_y)
print(test.mass)
print(test.distributed_loads_y[0][2] * test.length)

diameters = {0:10,100:15,400:10}
test2 = Shaft(500,diameters)
print(test2.diameter)
print(test2.mass)

test2.torque = 150000
test2.point_load_balance(0,500,0,0,0,0,1,1,20,test.torque, test.torque)
test2.get_distributed_loads()
print(test2.point_loads_y)


test2.add_stress_concentration(100,2)
print(test2.stress_concentrations)
print(test2.stress_factors)
test2.plot_shear_bending_diagrams('y')

'''test.torque = 540 * 1e3
test.point_load_balance(0,500,0,0,0,0,1,1,20,test.torque)
print(test.point_loads)

'''
N = test2.get_min_safety_factor()
print(N)

input_torque = 28000 / 1700 *np.pi / 30
print(input_torque)

d_in = {
    0: 20,
    40: 30,
    45: 20,
}

l_in = 189

ret_in = (87, 1)
should1_in = (40, 0.5)
should2_in = (45, 0.5)
key_in = (70)


d_1 = {
    0: 20,
    20: 30,
    81: 40,
    86: 30,
    135: 20,
}

d_2 = {
    
}

first_stage = Shaft(189, d_1)
first_stage.add_stress_concentration()


