from shaft_tables import *
from tables_values import *
import numpy as np
from numpy import pi
from Goodman_safety_factor_calculator import *
from Fatigue_strength_calculator import *
from baseStressCalculator import *

''' All values in SI units (mm, N, etc.), and keys are assumed to be
rectangular parallel keys, unless otherwise specified.'''

def interpolate_table_dimensions(table: dict, table_key: float):
    """Interpolates between the dimensionss stored in a dictionary, given that the dimensionss are of num type.
    Assumes the keys are increasing, such that the first key is of the lowest numerical dimensions.

    Args:
        table (dict): _description_
        table_key (float): _description_
    """
    selection = list(table.keys())
    error_message = "The input table_key is not within the bounds of the dictionary keys, being " + str(selection[0]) + "and" + str(selection[-1]) + "."
    a = float()
    for index in range(len(selection)):
        if table_key < selection[0] or table_key > selection[-1]:
            raise ValueError(error_message)
        elif table_key >= selection[index]:
            xp = [selection[index],selection[index-1]]
            fp = [table[i] for i in xp]
            a = float(np.interp(table_key,xp,fp))
    return a

def interpolate_table_tuple_pair(table: dict, table_key: float):
    """Interpolates between the dimensionss stored in a dictionary, given that the dimensionss are a 2-tuple.
    Assumes the keys are decreasing, such that the first key is of highest numerical dimensions.

    Args:
        table (dict): Dictionary containing the dimensionss to be interpolated.
        table_key (float): Key, or input, for which to interpolate the dimensions.

    Returns:
        tuple: 2-tuple containing the interpolated dimensionss for the corresponding key.
    """
    selection = list(table.keys())
    error_message = f"The input table_key is not within the bounds of the dictionary keys, being {selection[0]} and {selection[-1]}."
    a, b = float(), float()
    for index in range(len(selection)):
        if table_key > selection[0] or table_key < selection[-1]:
            raise ValueError(error_message)
        elif table_key >= selection[index]:
            xp = [selection[index], selection[index-1]]
            fp1, fp2 = [table[i][0] for i in xp], [table[i][1] for i in xp]
            a, b = float(np.interp(table_key,xp,fp1)), float(np.interp(table_key,xp,fp2))
    return (a,b)


class Shaft:
    pi = np.pi
    """By default, the shaft will be initialized as a steel shaft. These dimensionss will be input later."""
    def __init__(self, length, stresses, material_name, working, diameter):
        self.material = material_name
        self.Sy, self.Sut, self.HB, self.nu, self.E, self.G, self.rho = steels[material_name][working]
        self.length = length
        self.diameter = self._configure_diameter(diameter) # a bit annoying to pronounce
        self.volume = 0
        self.components = dict() # should the components be the keys or the dimensionss?
        self._stress_concentrations = dict()
        self._stress_factors = dict()
        self.rotating = False
        self.ang_speed = None
        self.stress_state = stresses # This should be standardized as the stresses at x = 0 (maybe, this would zero the 
        # moment in shear moment diagram)

    def __len__(self):
        return self.length

    def is_rotating(self,speed=0):
        self.rotating = True
        self.ang_speed = speed
    
    def _configure_diameter(self,diameter):
        """Configures the variation of diameter along the shaft into a dictionary.

        Args:
            diameter (dict or num): One or more shaft diameters, in numerical or dictionary form

        Returns:
            dict: Dictionary defining the variation in diameter of the Shaft
        """        
        if isinstance(diameter, dict):
            return diameter.update({self.length: list(diameter.dimensionss())[-1]})
        elif isinstance(diameter, (float, int)):
            return {0 : diameter, self.length : diameter}
    
    def add_stress_concentration(self, axial_pos: float, radius: float) -> None:
        """Adds a stress concentration, assuming a perfectly radial notch or fillet. 

        Ideally the function will not need diametrical inputs, I will fix this later - Simon
        
        Args:
            axial_pos (num): Position along the axis of the Shaft object to locate the stress concentration.
            radius (num): Radius of the stress concentration.
        """
        if axial_pos > self.length or axial_pos < 0:
            raise ValueError("The axial position of the stress concentration exceeds the length of the shaft.")

        isgroove = bool()
        initial_d = float()
        final_d = float()

        keys, values = zip(*self.diameter.items()) # Saw this trick online

        for index in range(len(keys)):
            if axial_pos not in self.diameter.keys():
                isgroove = True
                if axial_pos < keys[index]:
                    print("Since there is no change in diameter at this location, this will be interpreted as a groove.")
                    initial_d = values[index-1]
                    final_d = initial_d
                    break
            elif axial_pos == keys[index]:
                isgroove = False
                initial_d = values[index-1]
                final_d = values[index]
                break

        if 2 * radius > initial_d:
            raise ValueError("The assigned radius of the groove or fillet exceeds the diameter of the shaft.")
        
        # Storing the stress concentration values

        diameters = (initial_d, final_d)
        if isgroove:
            r, d, D = radius, max(diameters) - 2 * radius, max(diameters)
        else:
            r, d, D = radius, min(diameters), max(diameters)
        self._stress_concentrations[axial_pos] = (r, d, D)


        factors = dict()

        def set_kt_axial():
            """Calculates the stress concentration factor due to axial loading at the location of each stress concentration, 
            using the dimensions stored in self._stress_concentrations.
            """
            # need to also choose centering of the stress concentration for later consideration...
            if isgroove:
                a, b = interpolate_table_tuple_pair(kt_groove_tension, D / d)
            else:
                a, b = interpolate_table_tuple_pair(kt_shoulder_fillet_tension, D / d)
            factors["ktx"] = a * (r/d) ** b
            # The above statement could be removed if directly implemented in add_stress_concentration()

        def set_kt_bending():
            """Calculates the stress concentration factor due to bending at the location of each stress concentration, 
            using the dimensions stored in self._stress_concentrations.
            """            
            if isgroove:
                a, b = interpolate_table_tuple_pair(kt_groove_bending, D / d)
            else:
                a, b = interpolate_table_tuple_pair(kt_shoulder_fillet_bending, D / d)
            factors["ktb"] = a * (r/d) ** b
            # The above statement could be removed if directly implemented in add_stress_concentration()

        def set_kt_torsion():
            """Calculates the stress concentration factor due to torsion at the location of each stress concentration, 
            using the dimensions stored in self._stress_concentrations.
            """   
            if isgroove:
                a, b = interpolate_table_tuple_pair(kt_groove_tension, D / d)
            else:
                a, b = interpolate_table_tuple_pair(kt_shoulder_fillet_tension, D / d)
            factors["kts"] = a * (r/d) ** b

        def set_kf():
            """Calculates the fatigue stress concentration factor due to alternating stress at the location of each stress concentration, 
            using the dimensions stored in self._stress_concentrations.
            """   
            neuber_cnst = interpolate_table_dimensions(neuber_steel, self.Sut * 0.14504) # hard-coded for now
            q = 1 / (1 + neuber_cnst / np.sqrt(r))
            ktb = factors["ktb"]
            kts = factors["kts"]
            factors["kf"] = 1 + q * (ktb - 1)
            factors["kfs"] = 1 + q * (kts - 1)

        def set_km():
            return 0
        
        set_kt_axial()
        set_kt_bending()
        set_kt_torsion()
        set_kf() # Order is important
        set_km()

        self._stress_factors[axial_pos] = factors

        # I think it would actually be beneficial to change the scope of the stress factor functions: they should ideally 
        # only be called when stress concentration is being added.

    def add_keyseat(self):
        return
  
    def _get_sc(self):
        return self._stress_concentrations
    
    def _get_sf(self):
        return self._stress_factors

    stress_concentrations = property(
        fget = _get_sc,
        fset = None,
        fdel = None,
        doc = "The stress concentrations that appear on the shaft."
    )

    stress_factors = property(
        fget = _get_sf,
        fset = None,
        fdel = None,
        doc = "The stress concentration factors resulting from changes in cross-section."
    )

    def get_mass_of_shaft(self): # need to add the stress concentrations volume addition after
        """Calculates the mass (and thus the volume due to assumed homogeneity of the material) of the shaft.

        Returns: 
            (num): The mass of the shaft.
        """        
        vol = 0
        steps = list(self.diameter.keys())
        for index in range(len(steps)-1):
            l = steps[index+1] - steps[index]
            d = self.diameter[steps[index]]
            vol += 0.25 * l * pi * d ** 2
        for values in self.stress_concentrations.values():
            # Accounting for the volume created by the radii. This was calculated manually
            r, d, D = values
            washer = (2 * pi - pi ** 2 / 2 ) * d * r ** 2 + \
                (2 * pi - pi / 3 - pi ** 2 / 2) * r ** 3
            if d == D:
            # i.e. if it is a semi-circular groove, have to remove "two" radii
                vol -= 2 * washer
            else:
            # i.e. if it is a notch, only one to remove.
                vol += washer

        # Currently the volume is in cubic millimeters: now it will be converted to cubic meters.

        vol = round(vol * 1e-9, 5) # arbitrary accuracy
        self.volume = vol
        mass = vol * self.rho
        self.mass = mass
        return mass

def min_shaft_diameter(initial_guess, torque, tension, mass, length, Sy, Sut):
    """This is a very entry-level optimizer for the shaft. It assumes it is a simply supported beam
    at both ends, and that there are two supports positioned at the limits of the shafts. 

    This does not yet account for stress concentration factors.

    Args:
        initial_guess (_type_): _description_
        torque (_type_): _description_
        tension (_type_): _description_
        mass (_type_): _description_
        length (_type_): _description_
    """

    d = initial_guess
    reaction_force = mass * 9.81 / 2        
    bending_moment = length * reaction_force/ 2 # divided by the number of fixtures/bearings and the 
    # reaction force balance
    alt_bending = baseStressCalculator.bending_stress(bending_moment, d)
    mean_axial = baseStressCalculator.axial_stress(tension, d)
    mean_torque = baseStressCalculator.torsion_stress(torque, d)
    alt_shear = 0 # baseStressCalculator.transverse_shear(reaction_force, d)

    kf = 1
    kfs = 1
    kfm = 1
    kfsm = 1

    alt_tensor = np.array([[alt_bending, alt_shear, 0], [alt_shear, 0, 0],[0, 0, 0]])
    mean_tensor = np.array([[mean_axial, mean_torque, 0],[mean_torque, 0, 0],[0, 0, 0]])
    alternating_stress = baseStressCalculator.von_mises_equivalent(alt_tensor)
    mean_stress = baseStressCalculator.von_mises_equivalent(mean_tensor)
    Nf = GoodmanSafetyFactorCalculator.calc_safety_factor_case_1(Sy, alternating_stress, mean_stress)
    Sf = 0
    d = (32 * Nf / pi * (np.sqrt((kf * alt_bending) ** 2 + 3 / 4 * (kfs * alt_shear) ** 2) / Sf + \
                         np.sqrt((kfm * mean_axial) ** 2 + 3 / 4 * (kfsm * alt_bending) ** 2))) ** (1/3)
    

    return
"""some functions could be defined:

find critical points would return positions where the moment or shear is maximum, or where there are stress concentrations
Need a method of storing stress concentration features on the shaft
determine torque transfer and resulting velocity: done through the gear ratio
critical diameter of a shaft
critical length of a key
optimal gear ratio
safety factors! Or force safety factors dependent on case (see the slides for specific cases)
"""

# Should we define a subclass within the Shaft class as something like a ShaftAssembly? It would inherit the attributes but we could add that dictionary of components.
