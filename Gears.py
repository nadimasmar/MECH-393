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
    pinion = gear(module = 4.23e-3, num_teeth = 14, face_width=50.8e-3, quality_index=6, pressure_angle=25, 
                  torque=56.9, angular_velocity=261.8, sfb_prime=2.886e8, sfc_prime=813581361)
    idler = gear(module = 4.23e-3, num_teeth = 17, face_width=50.8e-3, quality_index=6, pressure_angle=25, 
                  torque=56.9*17/14, angular_velocity=261.8*14/17, sfb_prime=2.886e8, sfc_prime=813581361, idler=True)
    gear_ = gear(module = 4.23e-3, num_teeth = 49, face_width=50.8e-3, quality_index=6, pressure_angle=25, 
                  torque=56.9*49/14, angular_velocity=261.8*14/49, sfb_prime=2.886e8, sfc_prime=813581361)
    # print(pinion.calc_bending_stress(other_gear=idler)) # Correct
    # print(idler.calc_bending_stress(other_gear=pinion)) # Correct
    # print(gear_.calc_bending_stress(other_gear=idler)) #Correct. Close within 5%

    # Example 12-6 from lecture slides:
    # print(pinion.calc_surface_stress(other_gear=idler)) # Correct. Close within 2%
    # print(idler.calc_surface_stress(other_gear=pinion)) # Correct. Close within 2%.
    # print(gear_.calc_surface_stress(other_gear=idler)) # Correct. Close within 2%.

    #Example 12-7 from lecture slides:
    # print(pinion.calc_factor_of_safety(other_gear=idler)) # Correct. Close within 5%
    # print(idler.calc_factor_of_safety(other_gear=pinion)) # Correct.
    # print(gear_.calc_factor_of_safety(other_gear=idler)) # Correct. Close within 5%

    #Project Calcualtions
pinion = gear(module = 3.0e-3, num_teeth = 26, face_width=50.0e-3, quality_index=11, pressure_angle=20, 
                  torque=157.3, angular_velocity=178.02, sfb_prime=450e6, sfc_prime=1500e6)
gear_ = gear(module = 3.0e-3, num_teeth = 62, face_width=50.0e-3, quality_index=11, pressure_angle=20, 
                  torque=157.3*62/26, angular_velocity=178.02*26/62, sfb_prime=450e6, sfc_prime=1500e6)

print(pinion.calc_factor_of_safety(other_gear=gear_)) 
print(gear_.calc_factor_of_safety(other_gear=pinion))


