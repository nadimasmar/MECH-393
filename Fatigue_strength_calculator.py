'''This module defines a class for calculating the material fatigure strength of shatfs and keys. Gears are not included in this modules
because the fatigure strength of gears is determined using different factors and methodology

Note: Usage of this module should be reserbed to calling calc_corrected_fatigue_strength, which is the main method 
that calculates the corrected fatigue strength based on all factors.  The other methods are helper methods that 
calculate specific factors and should not be called directly by users of the module.
'''

import numpy as np

class FatigueStrengthCalculator:

    @staticmethod
    def C_size(object_type, dimensions):
        '''Calculate the size factor for fatigue strength based on the type of object and its dimensions.'''
        if object_type == "shaft":
            diameter = dimensions.get("diameter")
            if diameter is None:
                raise ValueError("Dimensions for shaft must include 'diameter'.")
            if diameter <= 8: # As specified in class, we assume C = 1 for shafts with diameter <= 8 mm
                return 1.0
            elif diameter > 8 and diameter <=250:
                return 1.189 * (diameter ** -0.097)
            elif diameter > 250:
                return 0.6
        
        elif object_type == "key":
            width = dimensions.get("width")
            length = dimensions.get("length")
            if width is None or length is None:
                raise ValueError("Dimensions for key must include 'width' and 'length'.")
            A_95 = width * length
            d_eq = np.sqrt(A_95/0.0766)
            if d_eq <= 8:
                return 1.0
            elif d_eq > 8 and d_eq <=250:
                return 1.189 * (d_eq ** -0.097)
            elif d_eq > 250:
                return 0.6
        
        else:
            raise ValueError("Unsupported object type. Must be 'shaft', or 'key'")
        
    @staticmethod
    def C_surface(surface_finish, S_ut):
        '''Calculate the surface finish factor C for fatigue strength based on surface finish.
        S_ut is the ultimate tensile strength in MPa. If C_surf greater than 1, it is set to 1'''
        if surface_finish == "ground":
            return np.min([1.58 * (S_ut ** -0.085), 1.0])
        elif surface_finish == "machined" or surface_finish == "cold-rolled":
            return np.min([4.51 * (S_ut ** -0.265), 1.0])
        elif surface_finish == "hot-rolled":
            return np.min([57.7 * (S_ut ** -0.718), 1.0])
        elif surface_finish == "as-forged":
            return np.min([272 * (S_ut ** -0.995), 1.0])

        else:
            raise ValueError("Unsupported surface finish. Must be 'ground', 'machined', 'cold-rolled', 'hot-rolled', or 'as-forged'.")
        
    @staticmethod
    def C_load(load_type):
        '''Calculate the load factor C for fatigue strength based on the type of loading.'''
        if load_type == "bending":
            return 1.0
        elif load_type == "axial":
            return 0.70
        elif load_type == "pure torsion":
            return 0.58
        else:
            raise ValueError("Unsupported load type. Must be 'bending', 'axial', or 'pure torsion'.")
    
    @staticmethod
    def C_reliab(reliability_percentage):
        '''Calculate the reliability factor C for fatigue strength based on the desired reliability percentage.'''
        reliability_factors = {
            50      : 1.0,
            90      : 0.897,
            95      : 0.868,
            99      : 0.814,
            99.9    : 0.753,
            99.99   : 0.702,
            99.999  : 0.659,
            99.9999 : 0.620
        }
        if reliability_percentage not in reliability_factors:
            raise ValueError("Unsupported reliability percentage. Must be one of: " + ", ".join(map(str, reliability_factors.keys())))
        return reliability_factors[reliability_percentage]
    
    @staticmethod
    def C_temp(temperature_celsius):
        '''Calculate the temperature factor C for fatigue strength based on the operating temperature in Celsius.'''
        if temperature_celsius <= 450:
            return 1.0
        elif temperature_celsius > 450 and temperature_celsius <= 550:
            return 1.0 - 0.0058 * (temperature_celsius - 450)
        else:
            raise ValueError("Unsupported temperature range. Must be below 550 degrees Celsius.")
        

    @staticmethod
    def calc_uncorrected_fatigue_strength(S_ut, material_type):
        '''Calculate the uncorrected fatigue strength based on the ultimate tensile strength and material type.'''
        if material_type == "steel":
            return np.min([0.5 * S_ut, 700])  
        
        elif material_type == "iron":
            return np.min([0.4 * S_ut, 160]) 
        
        elif material_type == "aluminum":
            return np.min([0.4 * S_ut, 130])
        
        elif material_type == "copper_alloy":
            return np.min([0.4 * S_ut, 100])
        
        else:
            raise ValueError("Unsupported material type. Must be 'steel', 'iron', 'aluminum', or 'copper_alloy'.")
        
    @staticmethod
    def calc_corrected_fatigue_strength(S_ut, material_type, object_type, dimensions, surface_finish, load_type, reliability_percentage, temperature_celsius):
        '''Calculate the corrected fatigue strength based on all factors.'''
        S_e_prime = FatigueStrengthCalculator.calc_uncorrected_fatigue_strength(S_ut, material_type)
        C_size = FatigueStrengthCalculator.C_size(object_type, dimensions)
        C_surface = FatigueStrengthCalculator.C_surface(surface_finish, S_ut)
        C_load = FatigueStrengthCalculator.C_load(load_type)
        C_reliab = FatigueStrengthCalculator.C_reliab(reliability_percentage)
        C_temp = FatigueStrengthCalculator.C_temp(temperature_celsius)

        S_e = S_e_prime * C_size * C_surface * C_load * C_reliab * C_temp
        return S_e