''' This module defines a class that calculates the Goodman safety factor depending on the applied stresses, material properties, 
and load case (1,2 or 3 as seen in class)

Note: Usage of this module is by calling the appropriate calc_safety_factor_case_X method. 

sigma_a: Alternating Von Mises stress in MPa
sigma_m: Mean Von Mises stress in MPa
S_y: Yield strength of the material in MPa
S_f: corrected fatigue strength of the material in MPa
S_ut: Ultimate tensile strength of the material in MPa
'''

class GoodmanSafetyFactorCalculator:
    @staticmethod
    def calc_safety_factor_case_1(S_y, sigma_a, sigma_m):
        '''Case 1: The alternating stress will remain constant over the life of the part but the mean stress can
        increase under service condition'''
        return (S_y / sigma_m) * (1 - (sigma_a / S_y))
    
    @staticmethod
    def calc_safety_factor_case_2(S_f, S_ut, sigma_a, sigma_m):
        '''Case 2: The mean stress will remain constant over the life of the part but the alternating stress can
        increase under service condition'''
        return (S_f / sigma_a) * (1 - (sigma_m / S_ut))
    
    @staticmethod
    def calc_safety_factor_case_3(S_f,S_ut, sigma_a, sigma_m):
        '''Case 3: Both alternating and mean stress components
        can increase under service conditions, but their ratio will remain constant.'''
        return (S_f * S_ut) / (sigma_a * S_ut + sigma_m * S_f)