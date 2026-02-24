import numpy as np
from keys_tables import *

''' All values in SI units (mm, N, etc.), and keys are assumed to be
rectangular parallel keys, unless otherwise specified.'''

class Key:
    def __init__(self, width, height, length):
        self.width = width
        self.height = height
        self.length = length

    def calc_shear_stress(self, torque, shaft_diameter):
        return (2 * torque) / (self.width * self.length * shaft_diameter)

    def calc_compressive_stress(self, torque, shaft_diameter):
        return (4 * torque) / (self.height * self.length * shaft_diameter)

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
        """Return (width_mm, height_mm) for rectangular keys based on shaft diameter in mm."""
        if not isinstance(shaft_diameter, (int, float)):
            raise TypeError("Shaft diameter must be a number in mm.")

        d = float(shaft_diameter)

        selection = list(std_rect_key_range_mm.keys())
        for index in range(len(selection)):
            if d < selection[index] and d > selection[0]:
                return std_rect_key_range_mm[selection[index-1]]
            raise ValueError("Shaft diameter out of supported range between 6 and 440 mm")