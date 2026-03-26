from Shaft import Shaft
test_shaft = Shaft(length=1.0, material_name=1020, working="cold rolled", diameter=1.3)
def run_distributed_load_check():
    # 1. Setup the object
    
    
    # 2. Assign the distributed load (start, end, mag)
    test_shaft.distributed_loads = {
        (0.0, 1.0, -15), 
    }
    
    # 3. Assign the point loads for static equilibrium
    test_shaft.point_loads = {
        (0.0, 5.0),  
        (0.25, 5.0), 
        (1.0, 5.0)   
    }    
    
    # 4. Print the output
    print("--- Distributed Load Moment Check ---")
    print(f"Moment at x=0.25 : {test_shaft.get_moment_at(0.25):8.3f} lbf-in")
    print(f"Moment at x=0.75 : {test_shaft.get_moment_at(0.75):8.3f} lbf-in")
    
    print(f"Shear at x=0.2 : {test_shaft.get_shear_at(0.2):8.3f} lbf")
    print(f"Shear at x=0.75 : {test_shaft.get_shear_at(0.75):8.3f} lbf")

if __name__ == "__main__":
    run_distributed_load_check()
    test_shaft.plot_shaft_diagrams(1000);