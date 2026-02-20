import numpy as np

''' All values in SI units (mm, N, etc.), and keys are assumed to be
rectangular parallel keys, unless otherwise specified.'''


def key_dimensions_from_shaft_diameter(shaft_diameter):
    """Return (width_mm, height_mm) for rectangular keys based on shaft diameter in mm."""
    if not isinstance(shaft_diameter, (int, float)):
        raise TypeError("Shaft diameter must be a number in mm.")

    d = float(shaft_diameter)

    if 8 < d <= 10:
        return (3, 3)
    if 10 < d <= 12:
        return (4, 4)
    if 12 < d <= 17:
        return (5, 5)
    if 17 < d <= 22:
        return (6, 6)
    if 22 < d <= 30:
        return (8, 7)
    if 30 < d <= 38:
        return (10, 8)
    if 38 < d <= 44:
        return (12, 8)
    if 44 < d <= 50:
        return (14, 9)
    if 50 < d <= 58:
        return (16, 10)
    if 58 < d <= 65:
        return (18, 11)
    if 65 < d <= 75:
        return (20, 12)
    if 75 < d <= 85:
        return (22, 14)
    if 85 < d <= 95:
        return (25, 14)

    raise ValueError("Shaft diameter out of supported range: 8 < d <= 95 mm.")


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
        ''' This static method calculates the stress concentration factors for end-milled keyseats in shafts
        under either bending or torsional loading. We assume assume radius to shaft diameter ratio of 0.021,
        as specified in ANSI standards. We also assume that the key is in place and transmitting torque.'''
        k_t = 2.2
        k_ts = 3.0
        return (k_t, k_ts)

    @staticmethod
    def key_dimensions_from_shaft_diameter(shaft_diameter, key_type="rectangular"):
        """Return Standard key (width_mm, height_mm) based on shaft diameter in mm."""
        if not isinstance(shaft_diameter, (int, float)):
            raise TypeError("Shaft diameter must be a number in mm.")
        
        if key_type != "rectangular":
            raise NotImplementedError(f"{key_type} keys are not supported. Only rectangular keys are currently supported.")

        d = float(shaft_diameter)

        if 8 < d <= 10:
            return (3, 3)
        if 10 < d <= 12:
            return (4, 4)
        if 12 < d <= 17:
            return (5, 5)
        if 17 < d <= 22:
            return (6, 6)
        if 22 < d <= 30:
            return (8, 7)
        if 30 < d <= 38:
            return (10, 8)
        if 38 < d <= 44:
            return (12, 8)
        if 44 < d <= 50:
            return (14, 9)
        if 50 < d <= 58:
            return (16, 10)
        if 58 < d <= 65:
            return (18, 11)
        if 65 < d <= 75:
            return (20, 12)
        if 75 < d <= 85:
            return (22, 14)
        if 85 < d <= 95:
            return (25, 14)

        raise ValueError("Shaft diameter out of supported range: 8 < d <= 95 mm.")
