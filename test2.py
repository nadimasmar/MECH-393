from Shaft import *

# create a shaft

test = Shaft(500,15)
print(test.length)
print(test.diameter)
test.set_distributed_loads()
print(test.distributed_loads)
print(test.mass)
print(test.distributed_loads[0][2] * test.length)

diameters = {0:10,100:15,400:10}
test2 = Shaft(500,diameters)
print(test2.diameter)
print(test2.mass)

test2.torque = 150000
test2.point_load_balance(0,500,0,0,0,0,1,1,20,test.torque)
test2.set_distributed_loads()
print(test2.point_loads)


test2.add_stress_concentration(100,2)
print(test2.stress_concentrations)
print(test2.stress_factors)

'''test.torque = 540 * 1e3
test.point_load_balance(0,500,0,0,0,0,1,1,20,test.torque)
print(test.point_loads)

'''
N = test2.get_min_safety_factor()
print(N)