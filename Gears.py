import numpy as np
import matplotlib.pyplot as plt


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
    def calc_bending_strength_factor(gear: "Gear", pinion: "Gear") -> tuple:
        # Assuming Full-Depth Teeth with HPSTC Loading

        if not isinstance(gear, Gear) or not isinstance(pinion, Gear):
            raise ValueError("Both gear and pinion must be instances of the Gear class.")
        
        if gear.num_teeth < pinion.num_teeth:
            raise ValueError("First input must be the gear, which has more teeth than the pinion.")
        
        if gear.pressure_angle != pinion.pressure_angle:
            raise ValueError("Both gear and pinion must have the same pressure angle.")
        
        J_table_20degrees = {
        (21, 21): (0.33, 0.33),
        (21, 26): (0.33, 0.35),
        (21, 35): (0.34, 0.37),
        (21, 55): (0.34, 0.40),
        (21, 135): (0.35, 0.43),

        (26, 26): (0.35, 0.35),
        (26, 35): (0.36, 0.38),
        (26, 55): (0.37, 0.41),
        (26, 135): (0.38, 0.44),

        (35, 35): (0.39, 0.39),
        (35, 55): (0.40, 0.42),
        (35, 135): (0.41, 0.45),

        (55, 55): (0.43, 0.43),
        (55, 135): (0.45, 0.47),

        (135, 135): (0.49, 0.49),
        }

        J_table_25degrees = {
        (14, 14): (0.33, 0.33),
        (14, 17): (0.33, 0.36),
        (14, 21): (0.33, 0.39),
        (14, 26): (0.33, 0.41),
        (14, 35): (0.34, 0.44),
        (14, 55): (0.34, 0.47),
        (14, 135): (0.35, 0.51),

        (17, 17): (0.36, 0.36),
        (17, 21): (0.36, 0.39),
        (17, 26): (0.37, 0.42),
        (17, 35): (0.37, 0.45),
        (17, 55): (0.38, 0.48),
        (17, 135): (0.38, 0.52),

        (21, 21): (0.39, 0.39),
        (21, 26): (0.40, 0.42),
        (21, 35): (0.40, 0.45),
        (21, 55): (0.41, 0.49),
        (21, 135): (0.42, 0.53),

        (26, 26): (0.43, 0.43),
        (26, 35): (0.43, 0.46),
        (26, 55): (0.44, 0.49),
        (26, 135): (0.45, 0.53),

        (35, 35): (0.46, 0.46),
        (35, 55): (0.47, 0.50),
        (35, 135): (0.48, 0.54),

        (55, 55): (0.51, 0.51),
        (55, 135): (0.53, 0.56),

        (135, 135): (0.57, 0.57),
        }

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
        

        

        
        
            

            

            
