import math
import numpy as np
import matplotlib.pyplot as plt
#from tables_values
from gears_tables import *
from interpolators import *

'''
externally calculated for now:  gear ratio mG, angvel.
'''    

class gear:
    def __init__(self, *, module, num_teeth, pressure_angle, face_width, quality_index, torque, angular_velocity,
                 sfb_prime, sfc_prime, idler=False):
        """
        Creates a Gear instance.

        Parameters
        ----------
        num_teeth           [dimensionless]
        pressure_angle      [degrees]               angle between line of action (slanted), and velocity (pitch circle tangent)
        module              [m]                     pitch diameter per tooth
        face_width          [m]
        quality_index       [?]                     uh
        torque              [N m]
        angular_velocity    [rad/s]

        Derived automatically:
        pitch_diameter, circular_pitch, base_pitch, diametral_pitch
        
        Raises
        ------
        Assertion Error
            If the provided number of teeth is too low to avoid undercutting for the provided gear pressure angle
        """
        # Preliminary initialization: required direct inputs
        self.module = module
        self.num_teeth = num_teeth
        self.pressure_angle = pressure_angle
        self.face_width = face_width
        self.quality_index = quality_index
        self.torque = torque
        self.angular_velocity = angular_velocity
        self.sfb_prime = sfb_prime
        self.sfc_prime = sfc_prime
        self.idler = idler

        # Derived geometry (directly computed from required inputs)
        self.pitch_diameter = self.module * self.num_teeth
        self.diametral_pitch = 1 / self.module
        self.circular_pitch = math.pi * self.module
        self.base_pitch = self.circular_pitch * math.cos(math.radians(self.pressure_angle))

        self.tooth_type = "full-depth"

        
    def check_undercutting(self):
        if self.num_teeth < 2/math.sin(math.radians(self.pressure_angle)):
            raise ValueError("number of teeth is under the minimum number of full-depth teeth! Undercutting will occur.")
        
    def calculate_perturbed_pressure_angle(self, pitch_radii_perturbation_percentage):
        try:
            pitch_radius = self.pitch_diameter/2
            numerator = pitch_radius*math.cos(math.radians(self.pressure_angle))
            denominator = (1+pitch_radii_perturbation_percentage/100) * pitch_radius
            return math.degrees(    math.acos(  numerator/denominator  )    )
        except TypeError:
            print("Unable to calculate perurbed pressure angle!")
                
    
    def info(self):
        for attr, value in self.__dict__.items():
            if value != None: print(f"{attr}: {value}")
        print("\n")
        
        try:
            if self.diametral_pitch < 20: print("Coarse Pitch")
            else: print("Fine Pitch")
        except: pass

    def calc_tangential_load(self):
            return 2*self.torque/self.pitch_diameter
    
    @staticmethod
    def calc_J(pinion_obj: "gear", gear_obj: "gear", load_condition="HPSTC") -> tuple:
        # Assuming Full-Depth Teeth with HPSTC Loading

        if not isinstance(gear_obj, gear) or not isinstance(pinion_obj, gear):
            raise ValueError("Both gear and pinion must be instances of the Gear class.")
        
        if gear_obj.num_teeth < pinion_obj.num_teeth:
            raise ValueError("First input must be the pinion, which has less teeth than the gear.")

        if gear_obj.pressure_angle != pinion_obj.pressure_angle:
            raise ValueError("Both gear and pinion must have the same pressure angle.")
        
        if gear_obj.module != pinion_obj.module:
            raise ValueError("Both gear and pinion must have the same module.")

        load_condition_map = {
            "HPSTC loading": "HPSTC",
            "HPSTC": "HPSTC",
            "tip loading": "tip loading",
        }
        tooth_type_map = {
            "full-depth": "full depth",
            "full depth": "full depth",
        }

        normalized_load = load_condition_map.get(load_condition, load_condition)
        normalized_tooth_type = tooth_type_map.get(pinion_obj.tooth_type, pinion_obj.tooth_type)

        try:
            table = J_table[pinion_obj.pressure_angle][normalized_tooth_type][normalized_load]
        except KeyError as exc:
            raise KeyError(
                "Unable to locate J_table selection for "
                f"pressure_angle={pinion_obj.pressure_angle}, "
                f"tooth_type='{normalized_tooth_type}', "
                f"load_condition='{normalized_load}'."
            ) from exc

        return interpolate_table_2tuple_tuple(table, (pinion_obj.num_teeth, gear_obj.num_teeth))
    
    def calc_ka(self):
        return 1.0 #assume smooth driven and driving machine
    
    def calc_km(self):
        table = face_factor
        face_width = self.face_width

        if face_width is None:
            raise ValueError("face_width must be specified to calculate Km.")

        bounds = tuple(table)
        low_bound = bounds[0]
        high_bound = bounds[-1]

        if face_width <= low_bound:
            return table[low_bound]
        if face_width >= high_bound:
            return table[high_bound]

        for i in range(1, len(bounds)):
            upper = bounds[i]
            if face_width <= upper:
                lower = bounds[i - 1]
                lower_value = table[lower]
                upper_value = table[upper]
                ratio = (face_width - lower) / (upper - lower)
                return lower_value + ratio * (upper_value - lower_value)
            
    
    def calc_kv(self):
        #k_v = (A/(A+sqrt(200v)))^B
        B = ((12 - self.quality_index)**(2/3)) / 4
        A = 50 + 56*(1-B)
        v = (self.pitch_diameter/2) * self.angular_velocity #m/s
        return (A/(A+np.sqrt(200*v)))**B
    
    def calc_kb(self):
        return 1.0 #assume solid gear
    
    def calc_ks(self):
        return 1.0 #assume no size effect
    
    def calc_ki(self):
        if self.idler == True:
            return 1.42
        else:
            return 1.0
    
    def calc_bending_stress(self, *, other_gear: "gear"):
        tangential_load = self.calc_tangential_load()
        if self.num_teeth < other_gear.num_teeth:
            pinion = self
            gear = other_gear
            J = self.calc_J(pinion_obj=pinion, gear_obj=gear)[0] 
        else:            
            pinion = other_gear
            gear = self
            J = self.calc_J(pinion_obj=pinion, gear_obj=gear)[1]
        ka = self.calc_ka()
        km = self.calc_km()
        kv = self.calc_kv()
        kb = self.calc_kb()
        ks = self.calc_ks()
        ki = self.calc_ki()
        return tangential_load * ka * km *  kb * ks * ki / (self.face_width * kv * self.module * J)


    def surface_geometry_factor(self, *, other_gear: "gear"):  
        if self.num_teeth < other_gear.num_teeth:
            pinion = self
            gear = other_gear
        else:            
            pinion = other_gear
            gear = self

        dp = pinion.pitch_diameter
        rp = dp / 2
        pd = pinion.diametral_pitch
        phi = pinion.pressure_angle
        C = rp + gear.pitch_diameter / 2

        radius_pinion = ((rp + 1 / pd) ** (2) - (rp * np.cos(np.radians(phi))) ** (2)) ** (0.5) - np.pi / pd * np.cos(np.radians(phi))
        radius_gear = C * np.sin(np.radians(phi)) - radius_pinion

        return np.cos(np.radians(phi)) / ((1 / radius_pinion + 1 / radius_gear) * dp)
    
    def calc_elastic_coefficient(self):
        return 191e3 #Pa, for steel. This is a placeholder, as we have not yet implemented material selection for gears. We will assume all gears are made of steel for now.
    
    def calc_surface_stress(self, *, other_gear: "gear"):
        tangential_load = self.calc_tangential_load()
        if self.num_teeth < other_gear.num_teeth:
            pinion = self
            gear = other_gear
        else:            
            pinion = other_gear
            gear = self        
        I = self.surface_geometry_factor(other_gear=other_gear)
        Cp = self.calc_elastic_coefficient()
        ka = self.calc_ka()
        km = self.calc_km()
        kv = self.calc_kv()
        ks = self.calc_ks()

        return Cp * np.sqrt(tangential_load * ka * km *  ks / (self.face_width * kv * I * pinion.pitch_diameter))
    
    def calc_KR(self):
        return 1.0 # We assume that we need a reliability of 99%.
    
    def calc_KT(self):
        return 1.0 # We assume that we are not applying any temperature derating to the gear.
    
    def calc_KL(self):
        return 1.0 # Assume life of 10^7 cycles. 

    def calc_Sfb(self):
        return self.sfb_prime * self.calc_KL() / (self.calc_KR() * self.calc_KT())
    
    def calc_CH(self):
        return 1.0 # Assume same material for pinion and gear.
    
    def calc_Sfc(self):
        return self.sfc_prime * self.calc_CH() * self.calc_KL() / (self.calc_KR() * self.calc_KT())
    
    def calc_bending_factor_of_safety(self, other_gear: "gear"):
        bending_stress = self.calc_bending_stress(other_gear=other_gear)
        Sfb = self.calc_Sfb()
        return Sfb / bending_stress 
    
    def calc_surface_factor_of_safety(self, other_gear: "gear"):
        Sfc = self.calc_Sfc()
        surface_stress = self.calc_surface_stress(other_gear=other_gear)
        return (Sfc / surface_stress) ** 2
    
    def calc_factor_of_safety(self, other_gear: "gear"):
        bending_fos = self.calc_bending_factor_of_safety(other_gear=other_gear)
        surface_fos = self.calc_surface_factor_of_safety(other_gear=other_gear)
        return bending_fos, surface_fos
    



if __name__ == "__main__":
    # Example 12-5 from lecture slides:
    #pinion = gear(module = 4.23e-3, num_teeth = 14, face_width=50.8e-3, quality_index=6, pressure_angle=25, 
    #              torque=56.9, angular_velocity=261.8, sfb_prime=2.886e8, sfc_prime=813581361)
    #idler = gear(module = 4.23e-3, num_teeth = 17, face_width=50.8e-3, quality_index=6, pressure_angle=25, 
    #              torque=56.9*17/14, angular_velocity=261.8*14/17, sfb_prime=2.886e8, sfc_prime=813581361, idler=True)
    #gear_ = gear(module = 4.23e-3, num_teeth = 49, face_width=50.8e-3, quality_index=6, pressure_angle=25, 
    #              torque=56.9*49/14, angular_velocity=261.8*14/49, sfb_prime=2.886e8, sfc_prime=813581361)
    # print(pinion.calc_bending_stress(other_gear=idler)) # Correct
    # print(idler.calc_bending_stress(other_gear=pinion)) # Correct
    # print(gear_.calc_bending_stress(other_gear=idler)) #Correct. Close within 5%

    # Example 12-6 from lecture slides:
    # print(pinion.calc_surface_stress(other_gear=idler)) # Correct. Close within 2%
    # print(idler.calc_surface_stress(other_gear=pinion)) # Correct. Close within 2%.
    # print(gear_.calc_surface_stress(other_gear=idler)) # Correct. Close within 2%.

    #Example 12-7 from lecture slides:
    #print(pinion.calc_factor_of_safety(other_gear=idler)) # Correct. Close within 5%
    #print(idler.calc_factor_of_safety(other_gear=pinion)) # Correct.
    #print(gear_.calc_factor_of_safety(other_gear=idler)) # Correct. Close within 5%

    #Heatmap Plotting
    #want to get two contour plots for bending and surface safety factors as a function of teeth number and face width.
    
    '''
    BRUTE FORCE CODE
    '''
    input_power = 28000 #W
    input_rpm = 1700 #rpm
    output_rpm = 300 #rpm
    tolerance = 0.05
    
    '''
    USER INPUT: Define number of stages
    '''
    num_stages = 2
    print("Number of stages:", num_stages)
    
    debug = False
    
    train_ratio = output_rpm/input_rpm
    stage_ratio = train_ratio**(1/num_stages) #this will be less than 1
    print("Nominal Train ratio", train_ratio)
    print("Nominal Stage ratio", stage_ratio)
    
    #Attempting to find good gear ratios
    PG_list = []
    for gear_num_teeth in range(1,100): #populate list with integer numbers of teeth
        pinion_num_teeth = round(gear_num_teeth * stage_ratio)
        PG_list.append((pinion_num_teeth, gear_num_teeth))
    if debug: print(PG_list)
    
    #conserves only combinations which are within tolerances
    acceptable_PG_combinations = []
    for PG_tuple in PG_list:
        pinion_num_teeth = PG_tuple[0]
        gear_num_teeth = PG_tuple[1]
        artificial_stage_ratio = pinion_num_teeth/gear_num_teeth
        artificial_train_ratio = artificial_stage_ratio**num_stages
        artificial_output_rpm = input_rpm * artificial_train_ratio
        error = (output_rpm-artificial_output_rpm)/output_rpm
        if abs(error) < tolerance:
            if pinion_num_teeth >= 14:
                acceptable_PG_combinations.append((pinion_num_teeth,gear_num_teeth))
        if debug: print(PG_tuple, "stage ratio:", artificial_train_ratio, "Output RPM:", artificial_output_rpm, "error%:", 100*round(error,5))
    print("GEAR COMBINATIONS WITHIN OUTPUT RPM:", output_rpm*(1-tolerance),"-", output_rpm*(1+tolerance))
    print(acceptable_PG_combinations)    
    
    '''
    USER INPUTS
    '''
    test_case = (24, 56) #pick these from the previously generated acceptable_PG_combinations list 
    quality_index = 11
    pressure_angle = 20
    modules = [0.5e-3, 1e-3, 1.5e-3, 2e-3, 2.5e-3, 3e-3, 3.5e-3, 4e-3, 4.5e-3, 5e-3] # 
    print("USER INPUT PARAMETERS:",
          "\n(P,G):",test_case,
          "\nQv:",quality_index,
          "\nPhi:",pressure_angle,
          "\nModule sweep range:",modules)
    
    '''
    PREP CODE FOR ITERATION
    '''
    #Figuring out Torques and angular velocities per stage
    input_w = input_rpm * 2*math.pi/60 #1 rev/min * 2pi rad/rev * 1 min/60s
    input_torque = input_power / input_w
    
    pinion_num_teeth = test_case[0]
    gear_num_teeth = test_case[1]
    
    artificial_velocity_ratio = pinion_num_teeth / gear_num_teeth
    artificial_torque_ratio = 1 / artificial_velocity_ratio
    if debug: print(artificial_stage_ratio)
    if debug: print(artificial_torque_ratio)
    
    stage_torques = [input_torque] #torques on each shaft
    torque = input_torque
    for i in range(num_stages):
        torque *= artificial_torque_ratio
        stage_torques.append(torque)
    if debug: print("Torques:",stage_torques) 
    
    stage_velocities_rpm = [input_rpm] #rpm of each shaft
    stage_velocities_w = [input_w] #angular velocity of each shaft
    rpm = input_rpm
    angvel = input_w
    for i in range(num_stages):
        rpm *= artificial_velocity_ratio
        angvel *= artificial_velocity_ratio
        stage_velocities_rpm.append(rpm)
        stage_velocities_w.append(angvel)
    if debug: print("RPM:", stage_velocities_rpm, '\nw:', stage_velocities_w)
    
    '''
    ITERATION
    '''
    optimization_results = [None for i in range(num_stages)]
    
    if True:
        for index in range(len(modules)):
            used_module = modules[index]
            #instantiating stage gears!
            '''
            NB: Stages are NOT the same as shafts!
            
            E.g. For a 2-stage:
             ____________________________________________________   
            |                                                   |
            |                    stage1         stage2          |
            |          | SHAFT 1        SHAFT 2        SHAFT 3  |
            | ---------+--------------------------------------- |
            | RPM:     | [1700,         721.2,         306.0]   |
            | Torques: | [157.3,        370.7,         873.9]   |
            |                                                   |
            | Gears:     pinion1 ------ gear1                   |
            |                          pinion2 -------- gear2   |
            |___________________________________________________|
                         
            Pinions start from index 0, and end before the last index.
            Gears start from index 1, and end at the last index.
            
            We care about pinions, since those have the highest stresses.
            So we'll instantiate the gears, and plot stresses for the pinions!
            '''
            gears = []
            for i in range(num_stages): #
                gears.append(gear(module = used_module,
                                  num_teeth = gear_num_teeth,
                                  face_width = 999, #gear face width will not be a limiting factor
                                  quality_index = quality_index,
                                  pressure_angle = pressure_angle,
                                  torque = stage_torques[i+1],
                                  angular_velocity = stage_velocities_w[i+1],
                                  sfb_prime=450e6,
                                  sfc_prime=1500e6))
            if False: 
                for i in range(len(gears)): 
                    gears[i].info()
            
            '''
            USER INPUT: SET PLOTTING BOUNDS
            '''
            min_teeth = 21 #y-axis, MAKE SURE THESE BOUNDS RESPECT THE MINIMUM TEETH # IN THE TABLES
            max_teeth = 50
            min_F_mm = 5 #x-axis
            max_F_mm = 100
            
            #initialize results array
            height = max_teeth - min_teeth +1
            width = max_F_mm - min_F_mm +1
            
            bending_results_array = np.zeros((height, width))
            surface_results_array = np.zeros((height, width))
            volume_array = np.zeros((height, width))
            F_m_quotient_array = np.zeros((height, width))     
            
            for stage in range(num_stages): #occurs once every stage
                for i in range(min_teeth, max_teeth+1): #iterate through teeth number (y-direction)
                
                    for j in range(min_F_mm,max_F_mm+1): #iterate through face width (x-direction)
                    
                        used_fw = j/1000
                        
                        test_pinion = gear(module = used_module, num_teeth = i, face_width=used_fw, quality_index=quality_index, pressure_angle=pressure_angle, 
                                      torque=stage_torques[stage], angular_velocity=stage_velocities_w[stage], sfb_prime=450e6, sfc_prime=1500e6)
                        
                        test_gear = gears[stage]
                        
                        bending_results_array[i-min_teeth][j-min_F_mm] = test_pinion.calc_factor_of_safety(other_gear=test_gear)[0]
                        surface_results_array[i-min_teeth][j-min_F_mm] = test_pinion.calc_factor_of_safety(other_gear=test_gear)[1]
                        
                        Area = math.pi*0.25*(test_pinion.pitch_diameter)**2
                        Volume = Area *  test_pinion.face_width
                        Volume_cm3 = Volume * 1000000
                        volume_array[i-min_teeth][j-min_F_mm] = Volume_cm3
                        
                        #we want F between 8/pd and 16/pd, or 8m and 16m. Therefore, F/m must be between 8 and 16!
                        F_m_quotient_array[i-min_teeth][j-min_F_mm] = test_pinion.face_width/test_pinion.module
            
                #print(bending_results_array)
                #print(surface_results_array)
                #print(volume_array)
                #print(F_m_quotient_array)
                
                if debug:
                    print("Stage", stage+1)
                    print("Shaft Torques:", stage_torques)
                    print("Shaft w:", stage_velocities_w)
                    print("pinion torque:", test_pinion.torque)
                    print("pinion w:", test_pinion.angular_velocity)
                    print("gear torque:", test_gear.torque)
                    print("gear w:", test_gear.angular_velocity)
                
                '''
                OBTAIN OPTIMAL VOLUME
                '''
                def optimize_volume(query_num_teeth, bend_array, surf_array, pdlimits_array, vol_array):
                    '''
                    Takes the results arrays generated by the plotting function, and computes the volume of a pinion with query_num_teeth that is over a safety factor of 2.5 
                    for both bending and surface stresses, and within recommended face width limits of 8/pd and 12/pd.
                    '''
                    numcols = len(bend_array[0])
                    
                    #find the row where the teeth_number matches the num_teeth (uses min_teeth, an external variable); essentially fixes the y position in the optimization problem to make it 1D
                    number_of_rows_to_increment = query_num_teeth - min_teeth 
                    bending_row_of_interest = bend_array[number_of_rows_to_increment]
                    surface_row_of_interest = surf_array[number_of_rows_to_increment]
                    pd_row_of_interest =  pdlimits_array[number_of_rows_to_increment]
                    volarray_row_of_interest = vol_array[number_of_rows_to_increment]
                    
                    if False:                    
                        print("At number of teeth:", query_num_teeth, '\n',
                              "Bending row:",bending_row_of_interest, '\n',
                              "Surface row:", surface_row_of_interest, '\n',
                              "F/m row:", pd_row_of_interest, '\n',
                              "Volume", volarray_row_of_interest)
                    
                    #with the relevant rows in all matrices, iterate through their values (increasing face width as we do so)
                    solution_exists_within_row = False
                    optimal_F = 0
                    for x in range(numcols):
                        #intialize booleans
                        valid_bending_safety_factor = False
                        valid_surface_safety_factor = False
                        valid_pd_range = False
                        #check conditions
                        if bending_row_of_interest[x] >= 2.5:
                            valid_bending_safety_factor = True
                        if surface_row_of_interest[x] >= 2.5:
                            valid_surface_safety_factor = True
                        if pd_row_of_interest[x] >= 8 and pd_row_of_interest[x] <= 16:
                            valid_pd_range = True                   
                        #escape condition
                        if valid_bending_safety_factor and valid_surface_safety_factor and valid_pd_range:
                            solution_exists_within_row = True
                            optimal_F = min_F_mm + x
                            optimal_volume = volarray_row_of_interest[x]
                            break
                    if solution_exists_within_row:    
                        return(query_num_teeth, optimal_F, optimal_volume)
                    else: return (query_num_teeth, None, None)
                optimized_N, optimized_F, optimal_volume = optimize_volume(pinion_num_teeth, bending_results_array, surface_results_array, F_m_quotient_array, volume_array)
                
                '''
                UPDATE BEST RESULTS DICTIONARY
                '''
                if not optimal_volume == None:
                    #compute volume of associated gear: from m = d/N, d = m * N
                    gear_d = used_module * test_case[1] # in m
                    gear_area = math.pi*0.25*(gear_d)**2 #in m2
                    gear_vol = gear_area* optimized_F 
                    gear_vol_cm3 = gear_vol * 1000
                    if optimization_results[stage] == None:
                        keys = ["Stage","Number of teeth","Face Width [mm]","Module [m]","Volume [cm^3]","Quality Index","Pressure Angle","Gear Volume"]
                        values = [stage+1, optimized_N, optimized_F, used_module, optimal_volume, quality_index, pressure_angle,gear_vol_cm3]
                        optimization_results[stage]=dict(zip(keys,values))
                    elif optimal_volume < optimization_results[stage]["Volume [cm^3]"]:
                        keys = ["Stage","Number of teeth","Face Width [mm]","Module [m]","Volume [cm^3]","Quality Index","Pressure Angle","Gear Volume"]
                        values = [stage+1, optimized_N, optimized_F, used_module, optimal_volume, quality_index, pressure_angle,gear_vol_cm3]  
                        optimization_results[stage]=dict(zip(keys,values))
                
                '''
                PlOTTING
                '''
                X = np.linspace(min_F_mm,max_F_mm,width)
                Y = np.linspace(min_teeth,max_teeth,height)
                
                levels = [0, 2.5]
                volume_levels = [100*i for i in range(0,9)]
                F_limit_levels = [8, 16]
                
                plt.contourf(X,Y,volume_array, volume_levels, cmap="Pastel1", extend="max")
                plt.colorbar(label='Volume [cm$^{3}$]', orientation="horizontal")
                plt.contour(X,Y,bending_results_array, levels, cmap="Blues", extend="neither") #bending stress safety factor
                #plt.colorbar(label='Bending Safety Factor')
                plt.contour(X,Y,surface_results_array, levels, cmap="Oranges", extend="neither")
                #plt.colorbar(label='Surface Safety Factor')
                plt.contour(X,Y,F_m_quotient_array, F_limit_levels, cmap="PiYG")
                plt.hlines(pinion_num_teeth, min_F_mm, max_F_mm, linestyles='dashdot', zorder=5)
                
                if not optimized_F == None: #mark optimal location and write data
                    plt.scatter(optimized_F, optimized_N, marker=7, s=75, zorder = 5)
                    caption = '(' + str(optimized_N) + ', ' + str(optimized_F) + ')' + '\n' + str(round(optimal_volume,1)) + "cm$^3$"
                    plt.annotate(caption, (optimized_F+3, optimized_N+1), bbox=dict(boxstyle='round,pad=0.2', fc='white', alpha=0.8))
                
                plt.title("Pinion Safety Factor\n"+
                          #"Optimized Volume =" + optimal_volume + " cm^3\n" +
                          "Module = " + str(used_module*1000) + " mm" +
                          "\nPressure Angle = " + str(test_pinion.pressure_angle) +
                          "\nGear #Teeth = " + str(test_gear.num_teeth) +
                          "; Target Pinion #Teeth = " + str(pinion_num_teeth) +               
                          "\nStage = " + str(stage+1) + " of " + str(num_stages) +
                          "\nPinion Torque = " + str(round(test_pinion.torque, 1)) + " N$\cdot$m" +
                          "; Gear Torque = " + str(round(test_gear.torque, 1)) + " N$\cdot$m" +
                          "\nPinion \u03C9 = " + str(round(test_pinion.angular_velocity, 1)) + " rad/s" +
                          "; Gear \u03C9 = " + str(round(test_gear.angular_velocity, 1)) + " rad/s"
                          )
                #add info on the gear angular velocities and torques 
                plt.ylabel('Number of teeth')
                plt.xlabel('Face Width [mm]')
                
                y_tick_spacing = 1
                x_tick_spacing = 5
                #plt.yticks(np.arange(min_teeth, max_teeth+1, y_tick_spacing))
                plt.xticks(np.arange(min_F_mm, max_F_mm, x_tick_spacing))
                plt.grid("show", color="gray", linewidth=0.5)
                
                plt.show()
        
        '''
        PRINTING OPTIMIZATION RESULTS
        '''
        print('\n----------------RESULTS------------------')
        for i in optimization_results: #display result dictionaries
            for key, value in i.items():
                print(f"{key}: {value}")
            print('-')
        total_volume = 0
        for i in optimization_results: #display total gear volume
            total_volume += i["Volume [cm^3]"]
            total_volume += i["Gear Volume"]
        print("Total Pinion Volume:", total_volume, "cm^3")
            
        
            
#---------------------------------------------------------------------------------------------------    
    if False:
        for index in range(len(modules)):
            used_module = modules[index]
            
            pinion_num_teeth = 26
            torque = [157.3, 891.2676813]
            pinion = gear(module = used_module, num_teeth = pinion_num_teeth, face_width=50.0e-3, quality_index=11, pressure_angle=20, 
                          torque=157.3, angular_velocity=178.02, sfb_prime=450e6, sfc_prime=1500e6)
            
            #set plotting bounds
            min_teeth = 40 #y-axis
            max_teeth = 60
            min_F_mm = 1 #x-axis
            max_F_mm = 100
            
            #initialize results array
            height = max_teeth - min_teeth +1
            width = max_F_mm - min_F_mm +1
            
            bending_results_array = np.zeros((height, width))
            surface_results_array = np.zeros((height, width))
            volume_array = np.zeros((height, width))
            F_m_quotient_array = np.zeros((height, width))
            
            for i in range(min_teeth, max_teeth+1): #iterate through teeth number (y-direction)
            
                for j in range(min_F_mm,max_F_mm+1): #iterate through face width (x-direction)
                
                    used_fw = j/1000
                    
                    test_gear = gear(module = used_module, num_teeth = i, face_width=used_fw, quality_index=11, pressure_angle=20, 
                                  torque=157.3*62/26, angular_velocity=178.02*26/62, sfb_prime=450e6, sfc_prime=1500e6)
                    
                    bending_results_array[i-min_teeth][j-min_F_mm] = test_gear.calc_factor_of_safety(other_gear=pinion)[0]
                    surface_results_array[i-min_teeth][j-min_F_mm] = test_gear.calc_factor_of_safety(other_gear=pinion)[1]
                    
                    Area = math.pi*0.25*(test_gear.pitch_diameter)**2
                    Volume = Area *  test_gear.face_width
                    Volume_cm3 = Volume * 1000000
                    volume_array[i-min_teeth][j-min_F_mm] = Volume_cm3
                    
                    #we want F between 8/pd and 16/pd, or 8m and 16m. Therefore, F/m must be between 8 and 16!
                    F_m_quotient_array[i-min_teeth][j-min_F_mm] = test_gear.face_width/test_gear.module
            
            print(bending_results_array)
            print(surface_results_array)
            print(volume_array)
            print(F_m_quotient_array)
            
            
            #plotting
            X = np.linspace(min_F_mm,max_F_mm,width)
            Y = np.linspace(min_teeth,max_teeth,height)
            
            levels = [0, 2.5]
            volume_levels = [300*i for i in range(0,9)]
            F_limit_levels = [8, 16]
            
            plt.contourf(X,Y,volume_array, volume_levels, cmap="Pastel1", extend="max")
            plt.colorbar(label='Volume [cm^3]', orientation="horizontal")
            plt.contour(X,Y,bending_results_array, levels, cmap="Blues", extend="neither", label="bending")
            #plt.colorbar(label='Bending Safety Factor')
            plt.contour(X,Y,surface_results_array, levels, cmap="Oranges", extend="neither", label="surface")
            #plt.colorbar(label='Surface Safety Factor')
            plt.contour(X,Y,F_m_quotient_array, F_limit_levels, cmap="PiYG")
        
            
            plt.title("Gear Safety Factor\n"+"Module = " + str(used_module*1000) + " mm" + "\nPinion #Teeth = " + str(pinion_num_teeth))
            plt.ylabel('Number of teeth')
            plt.xlabel('Face Width [mm]')
            
            y_tick_spacing = 2
            #x_tick_spacing = 0.5
            plt.yticks(np.arange(min_teeth, max_teeth+1, y_tick_spacing))
            #plt.xticks(np.arange(min_F_mm, max_F_mm, x_tick_spacing))
            plt.grid("show", color="gray", linewidth=0.5)
            
            plt.show()