from Shaft import Shaft

def run_realistic_scenario():
    # 1. Setup the object (10-inch shaft)
    test_shaft = Shaft(length=10.0, material_name=4140, working="tempered 400", diameter=0.75)
    
    # Apply a constant torque of 250 lbf-in (transmitting power between the gears)
    test_shaft.torque = 250.0 
    
    # 2. Configure Realistic Diameters (Stepped Shaft)
    # The shaft is 0.75" at the bearings, but steps up to 1.2" in the middle to hold the gears.
    test_shaft.diameter = {
        0.0: 0.75,   # Left bearing journal
        2.0: 1.20,   # Step up for gear section
        8.0: 0.75    # Step down for right bearing journal
    }
    
    # 3. Y-Axis Loads (Radial gear forces and bearing reactions)
    test_shaft.point_loads_y = {
        (0.0, 340.0),   # Left Bearing Reaction (Up)
        (3.0, -400.0),  # Gear 1 pushing down
        (7.0, -200.0),  # Gear 2 pushing down
        (10.0, 260.0)   # Right Bearing Reaction (Up)
    }
    test_shaft.distributed_loads_y = set() 
    
    # 4. Z-Axis Loads (Tangential gear forces and bearing reactions)
    test_shaft.point_loads_z = {
        (0.0, -90.0),   # Left Bearing Reaction
        (3.0, 150.0),   # Gear 1 pushing out
        (7.0, -50.0),   # Gear 2 pushing in
        (10.0, -10.0)   # Right Bearing Reaction
    }
    test_shaft.distributed_loads_z = set()

    # 5. Apply Stress Concentrations
    # These must be injected directly into your internal dictionary for this test
    # (Assuming your _stress_factors dict is structured like {position: {"ktb": val, "kts": val}})
    test_shaft._stress_factors = {
        # Fillets at the diameter steps
        2.0: {"ktb": 1.5, "kts": 1.3},
        8.0: {"ktb": 1.5, "kts": 1.3},
        
        # Profile keyways cut into the shaft to hold the gears at x=3 and x=7
        3.0: {"ktb": 2.14, "kts": 3.0},
        7.0: {"ktb": 2.14, "kts": 3.0}
    }

    # 6. Run the plotting function
    print("Generating Realistic Shaft Diagrams...")
    
    # Using von Mises since 1020 steel is ductile
    test_shaft.plot_shaft_diagrams(num_points=2000, failure_theory="von_mises")

if __name__ == "__main__":
    run_realistic_scenario()