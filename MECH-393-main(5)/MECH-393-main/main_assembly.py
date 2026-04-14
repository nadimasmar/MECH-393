import numpy as np

# Import your three individual stages
import two_stage_input as stage1
import two_stage_inter as stage2
import two_stage_output as stage3

from Shaft import calculate_system_phase_shift

print("\n" + "="*50)
print("     FULL GEARBOX SYSTEM ANALYSIS & DIAGNOSTICS    ")
print("="*50 + "\n")

# ---------------------------------------------------------
# 1. TOTAL MASS CALCULATION
# ---------------------------------------------------------
total_mass = stage1.input_shaft.mass + stage2.inter_shaft.mass + stage3.output_shaft.mass
print(f"Total Shaft Assembly Mass: {total_mass:.3f} kg\n")


# ---------------------------------------------------------
# 2. SYSTEM PHASE SHIFT (TORSIONAL WINDUP)
# ---------------------------------------------------------
# Ratios: (Driving Pitch Diameter / Driven Pitch Diameter)
ratio_1 = stage1.input_gear_pitch_d / stage2.gear_1_diameter  # 72 / 168
ratio_2 = stage2.gear_2_diameter / stage3.gear_1_diameter     # 96 / 224

total_windup_rad = calculate_system_phase_shift(
    (stage1.input_shaft, stage1.input_gear_pos, ratio_1),  
    (stage2.inter_shaft, stage2.gear_2_pos, ratio_2),      
    (stage3.output_shaft, stage3.gear_2_pos)               
)

total_windup_deg = np.rad2deg(total_windup_rad)
print(f"Total Output Phase Shift: {total_windup_rad:.6f} rad ({total_windup_deg:.4f}°)\n")

# ---------------------------------------------------------
# 3. KINEMATICS & EXCITATION FREQUENCIES
# ---------------------------------------------------------
# Define the gear teeth based on your pitch diameters
teeth_input = 24       # 72mm diameter (Module 3)
teeth_inter_in = 56    # 168mm diameter
teeth_inter_out = 24   # 96mm diameter (Module 4)
teeth_output = 56      # 224mm diameter

# Calculate the RPM of each shaft based on the gear reductions
rpm_input = 1750.0
rpm_inter = rpm_input * ratio_1
rpm_output = rpm_inter * ratio_2

# Calculate the shared Gear Mesh Frequencies (GMF) for each stage in Hz
# GMF = (RPM / 60) * Number of Teeth
gmf_stage_1 = (rpm_input / 60.0) * teeth_input
gmf_stage_2 = (rpm_inter / 60.0) * teeth_inter_out

print("-" * 40)
print("   KINEMATICS & EXCITATION SUMMARY   ")
print("-" * 40)
print(f"Input Shaft Speed  : {rpm_input:.1f} RPM ({(rpm_input/60):.2f} Hz)")
print(f"Inter Shaft Speed  : {rpm_inter:.1f} RPM ({(rpm_inter/60):.2f} Hz)")
print(f"Output Shaft Speed : {rpm_output:.1f} RPM ({(rpm_output/60):.2f} Hz)")
print(f"Stage 1 GMF        : {gmf_stage_1:.2f} Hz (Felt by Input & Inter shafts)")
print(f"Stage 2 GMF        : {gmf_stage_2:.2f} Hz (Felt by Inter & Output shafts)\n")


# ---------------------------------------------------------
# 4. INDIVIDUAL SHAFT RESONANCE CHECKS
# ---------------------------------------------------------
# Helper function to approximate inertia of a solid steel gear: J = 1/8 * m * D^2
def get_inertia(mass_kg, diameter_mm):
    return 0.125 * mass_kg * ((diameter_mm / 1000.0) ** 2)

# --- A. INPUT SHAFT --- (Experiences Stage 1 GMF)
inertia_input = get_inertia(stage1.input_gear_mass, stage1.input_gear_pitch_d)
danger_in, report_in = stage1.input_shaft.check_torsional_resonance(
    evaluate_x=stage1.input_gear_pos, 
    gear_inertia_kgm2=inertia_input, 
    operating_rpm=rpm_input,
    num_teeth=teeth_input
)

# --- B. INTERMEDIATE SHAFT --- (Experiences Stage 1 AND Stage 2 GMFs)
inertia_inter = get_inertia(stage2.gear_1_mass, stage2.gear_1_diameter) + \
                get_inertia(stage2.gear_2_mass, stage2.gear_2_diameter)

# We check against teeth_inter_in (56) because it generates the higher, more dangerous GMF
# --- B. INTERMEDIATE SHAFT ---
danger_mid, report_mid = stage2.inter_shaft.check_torsional_resonance(
    evaluate_x=stage2.gear_2_pos,  # <--- Change this to gear_2_pos
    gear_inertia_kgm2=inertia_inter, 
    operating_rpm=rpm_inter,
    num_teeth=teeth_inter_in 
)

# --- C. OUTPUT SHAFT --- (Experiences Stage 2 GMF)
inertia_output = get_inertia(stage3.gear_1_mass, stage3.gear_1_diameter)
# --- C. OUTPUT SHAFT ---
danger_out, report_out = stage3.output_shaft.check_torsional_resonance(
    evaluate_x=stage3.gear_2_pos,  # <--- Change this to gear_2_pos
    gear_inertia_kgm2=inertia_output, 
    operating_rpm=rpm_output,
    num_teeth=teeth_output
)

print("INPUT SHAFT " + report_in)
print("\nINTERMEDIATE SHAFT " + report_mid)
print("\nOUTPUT SHAFT " + report_out)

print("\n" + "="*50)