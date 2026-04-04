import numpy as np
from keys_tables import *
from Fatigue_strength_calculator import FatigueStrengthCalculator

''' All values in SI units (mm, N, etc.), and keys are assumed to be
rectangular parallel keys, unless otherwise specified.'''

class Key:
    def __init__(self, *, width, height, length, mean_torque, alternating_torque, Sut, Sf_prime, Sy):
        self.width = width
        self.height = height
        self.length = length

        self.mean_torque = mean_torque
        self.alternating_torque = alternating_torque

        self.Sut = Sut
        self.Sf_prime = Sf_prime
        self.Sy = Sy



    def calc_shear_stresses(self, shaft_diameter):
        tau_mean = (2 * self.mean_torque) / (self.width * self.length * shaft_diameter)
        tau_alt = (2 * self.alternating_torque) / (self.width * self.length * shaft_diameter)
        return tau_mean, tau_alt


    def calc_compressive_stress(self, shaft_diameter):
        sigma = (4 * (self.mean_torque+self.alternating_torque)) / (self.height * self.length * shaft_diameter)
        return sigma

    def calc_von_mises_stress(self, tau_mean, tau_alt):
        sigma_vm_mean = np.sqrt(3.0) * tau_mean
        sigma_vm_alt = np.sqrt(3.0) * tau_alt
        return sigma_vm_mean, sigma_vm_alt
    
    def calc_fatigue_strength(self):
        C_size = FatigueStrengthCalculator.C_size("key", {"width": self.width, "length": self.length})
        C_surface = FatigueStrengthCalculator.C_surface("cold-rolled", self.Sut*1e-6) # Convert to MPa for the surface factor calculation
        C_load = FatigueStrengthCalculator.C_load("bending")
        C_temp = FatigueStrengthCalculator.C_temp(25) # Assuming room temperature of 25 degrees Celsius  
        C_reliability = FatigueStrengthCalculator.C_reliab(99) # Assuming 99% reliability
        Sf = self.Sf_prime * C_size * C_surface * C_load * C_reliability * C_temp
        return Sf
    
    def calc_safety_factor(self, shaft_diameter):
        tau_mean, tau_alt = self.calc_shear_stresses(shaft_diameter)
        sigma_vm_mean, sigma_vm_alt = self.calc_von_mises_stress(tau_mean, tau_alt)
        Sf = self.calc_fatigue_strength()
        fatigue_safety_factor = (Sf * self.Sut) / (self.Sut * sigma_vm_alt + Sf * sigma_vm_mean)
        bearing_safety_factor = self.Sy / self.calc_compressive_stress(shaft_diameter)
        return fatigue_safety_factor, bearing_safety_factor

    @staticmethod
    def stress_concentration_factor():
        """This static method calculates the stress concentration factors for end-milled keyseats in shafts
        under either bending or torsional loading. We assume assume radius to shaft diameter ratio of 0.021,
        as specified in ANSI standards. We also assume that the key is in place and transmitting torque.

        Returns:
            tuple: Pair of tensile and torsional stress concentration factors, respectively.
        """
        k_t = 2.2
        k_ts = 3.0
        return (k_t, k_ts)

    @staticmethod
    def key_dimensions_from_shaft_diameter_sqr(shaft_diameter):
        """Return (width_mm, height_mm) for square keys based on shaft diameter in mm.

        Args:
            shaft_diameter (num): Diameter of the shaft to be keyed.

        Raises:
            TypeError: Crashes if argument is not of type num
            ValueError: Crashes if an invalid key is used outside the accepted range

        Returns:
            tuple: Pair of width and height, respectively
        """
        if not isinstance(shaft_diameter, (int, float)):
            raise TypeError("Shaft diameter must be a number in mm.")

        d = float(shaft_diameter)

        selection = list(std_square_key_range_mm.keys())
        for index in range(len(selection)):
            if d < selection[index] and d > selection[0]:
                return std_square_key_range_mm[selection[index-1]]
            raise ValueError("Shaft diameter out of supported range between 6 and 440 mm")

    @staticmethod
    def key_dimensions_from_shaft_diameter_rect(shaft_diameter):
        """Return (width_mm, height_mm) for rectangular keys based on shaft diameter in mm.
        
        Args:
            shaft_diameter (num): Diameter of the shaft to be keyed.
        
        Raises:
            TypeError: Crashes if argument is not of type num
            ValueError: Crashes if an invalid key is used outside the accepted range
        
        Returns:
            tuple: Pair of width and height, respectively
        """
        if not isinstance(shaft_diameter, (int, float)):
            raise TypeError("Shaft diameter must be a number in mm.")

        d = float(shaft_diameter)

        selection = list(std_rect_key_range_mm.keys())
        for index in range(len(selection)):
            if d < selection[index] and d > selection[0]:
                return std_rect_key_range_mm[selection[index-1]]
            raise ValueError("Shaft diameter out of supported range between 6 and 440 mm")
        

if __name__ == "__main__":
    # Lecture 10 Example 10-4
    key = Key(width=4.7498e-3, height=4.7498e-3, length=12.7e-3, mean_torque=8.25, alternating_torque=8.25, Sut=3.654e8, Sf_prime=0.5*3.654e8, Sy=3.034e8)
    fatigue_safety_factor, bearing_safety_factor = key.calc_safety_factor(shaft_diameter=19.05e-3)
    print(f"Fatigue Safety Factor: {fatigue_safety_factor:.2f}") 
    print(f"Bearing Safety Factor: {bearing_safety_factor:.2f}")