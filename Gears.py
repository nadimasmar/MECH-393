import numpy as np
import matplotlib.pyplot as plt
from tables_values import J_table_20degrees, J_table_25degrees

class Gear:
    def __init__(self, module, num_teeth, pressure_angle, face_width, quality_index):
        self.module = module
        self.num_teeth = num_teeth
        self.pressure_angle = pressure_angle
        self.face_width = face_width
        self.quality_index = quality_index

        self.pitch_diameter = self.__calc_pitch_diameter()

    def __calc_pitch_diameter(self):
        return self.module * self.num_teeth
    
    def __calc_tangential_force(self, torque):
        return 2 * torque / self.pitch_diameter
    
    def __calc_radial_force(self, tangential_force):
        return tangential_force * np.tan(np.radians(self.pressure_angle))
    
    @staticmethod
    def calc_bending_strength_factor(gear: "Gear", pinion: "Gear") -> dict:
        # Assuming Full-Depth Teeth with HPSTC Loading

        if not isinstance(gear, Gear) or not isinstance(pinion, Gear):
            raise ValueError("Both gear and pinion must be instances of the Gear class.")
        
        if gear.num_teeth < pinion.num_teeth:
            raise ValueError("First input must be the gear, which has more teeth than the pinion.")
        
        if gear.pressure_angle != pinion.pressure_angle:
            raise ValueError("Both gear and pinion must have the same pressure angle.")

        if gear.pressure_angle == 20:
            J_table = J_table_20degrees
            vals = J_table.get((pinion.num_teeth, gear.num_teeth))
            if vals is None:
                raise ValueError("Invalid combination of teeth numbers for 20 degree pressure angle.")
            return vals
        
        elif gear.pressure_angle == 25:
            J_table = J_table_25degrees
            vals = J_table.get((pinion.num_teeth, gear.num_teeth))
            if vals is None:
                raise ValueError("Invalid combination of teeth numbers for 25 degree pressure angle.")
            return vals
        

        

        
        
            

            

            
