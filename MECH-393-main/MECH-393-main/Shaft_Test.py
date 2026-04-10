import numpy as np
from Shaft import Shaft

def run_torsion_test():
    # Define a stepped shaft to verify the section-by-section integration logic.
    # 25mm diameter for the first 100mm, 20mm diameter for the rest.
    diameter_profile = {0.0: 25.0, 100.0: 20.0, 200.0: 20.0}
    
    # Initialize the shaft. Length is 200mm.
    test_shaft = Shaft(length=200.0, diameter=diameter_profile, material_name=1020, working="cold rolled")
    
    # Apply a realistic torque: 50,000 N-mm (~50 N-m) applied from x=50 to x=150.
    # This spans across the step in the diameter.
    test_shaft.torque = (50.0, 150.0, 50000)
    
    print("--- Torsional Deflection Test ---")
    
    # 1. Test total phase angle across the entire torque span
    total_twist_rad = test_shaft.get_phase_angle_at(200.0)
    print(f"Total Phase Angle: {total_twist_rad:.6e} rad ({np.rad2deg(total_twist_rad):.4f}°)")
    
    # 2. Test phase angle at specific locations to verify accumulation
    test_points = [0.0, 50.0, 100.0, 150.0, 200.0]
    print("\n--- Deflection at Specific Points ---")
    for x in test_points:
        twist_rad = test_shaft.get_phase_angle_at(x)
        print(f"Twist at x={x:5.1f} mm: {twist_rad:.6e} rad ({np.rad2deg(twist_rad):.4f}°)")

    # 3. Test the limit verification sweep function
    print("\n--- Limit Verification ---")
    print("Testing against 0.5° limit (Should Pass):")
    test_shaft.check_torsional_deflection_limits(max_allowed_degrees=0.5, num_points=100)
    
    print("\nTesting against 0.1° limit (Should Fail):")
    test_shaft.check_torsional_deflection_limits(max_allowed_degrees=0.1, num_points=100)

if __name__ == "__main__":
    run_torsion_test()