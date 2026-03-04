from shaft_tables import *
from tables_values import *
import numpy as np

def interpolate_table_value(table: dict, table_key: float):
    """Interpolates between the values stored in a dictionary, given that the values are of num type.
    Assumes the keys are increasing, such that the first key is of the lowest numerical value.

    Args:
        table (dict): _description_
        table_key (float): _description_
    """
    error_message = f"The input table_key is not within the bounds of the dictionary keys, being {selection[0]} and {selection[-1]}."
    selection = list(table.keys)
    a = float()
    for index in range(len(selection)):
        if table_key < selection[0] or table_key > selection[-1]:
            raise ValueError(error_message)
        elif table_key >= selection[index]:
            xp = [selection[index],selection[index-1]]
            fp = [table[i] for i in xp]
            a = np.interp(table_key,xp,fp)
    return a

def interpolate_table_tuple_pair(table: dict, table_key: float):
    """Interpolates between the values stored in a dictionary, given that the values are a 2-tuple.
    Assumes the keys are decreasing, such that the first key is of highest numerical value.

    Args:
        table (dict): Dictionary containing the values to be interpolated.
        table_key (float): Key, or input, for which to interpolate the value.

    Returns:
        tuple: 2-tuple containing the interpolated values for the corresponding key.
    """
    error_message = f"The input table_key is not within the bounds of the dictionary keys, being {selection[0]} and {selection[-1]}."
    selection = list(table.keys())
    a, b = float(), float()
    for index in range(len(selection)):
        if table_key > selection[0] or table_key < selection[-1]:
            raise ValueError(error_message)
        elif table_key >= selection[index]:
            xp = [selection[index], selection[index-1]]
            fp1, fp2 = [table[i][0] for i in xp], [table[i][1] for i in xp]
            a, b = np.interp(table_key,xp,fp1), np.interp(table_key,xp,fp2)
    return (a,b)


class Shaft:
    """By default, the shaft will be initialized as a steel shaft. These values will be input later."""
    def __init__(self, length, stresses, material_name, diameter):
        self.material = material_name
        self.Sy, self.Sut, self.HB, self.nu, self.E, self.G, self.rho = steels[material_name]
        self.length = length
        self.diameter = self.configure_diameter(diameter) # a bit annoying to pronounce
        self.volume = 0
        self.components = dict() # should the components be the keys or the values?
        self._stress_concentrations = dict()
        self._stress_factors = dict()
        self.rotating = False
        self.ang_speed = None
        self.stress_state = stresses # This should be standardized as the stresses at x = 0 (maybe, this would zero the 
        # moment in shear moment diagram)

    def __len__(self):
        return self.length
    
    def __str__(self):
        string = ""
        string.append(f"A {self.material}, {len(self)}-long shaft")
        gear_num = sum([isinstance(x) for x in self.components.keys()])
        if gear_num > 0:
            # need a way to get the positions of the gears. not necessary right now
            string.append(f" with {gear_num} gears at {self.components[2]}")

    def is_rotating(self,speed=0):
        self.rotating = True
        self.ang_speed = speed
    
    def configure_diameter(self,diameter):
        """Configures the variation of diameter along the shaft into a dictionary.

        Args:
            diameter (dict or num): One or more shaft diameters, in numerical or dictionary form

        Returns:
            dict: Dictionary defining the variation in diameter of the Shaft
        """        
        if isinstance(diameter, dict):
            return diameter.update({self.length,list(diameter.values())[-1]})
        elif isinstance(diameter, (float, int)):
            return {0 : diameter, self.length : diameter}
    
    def add_stress_concentration(self, axial_pos: float, radius: float, initial_d: float, final_d=None):
        """Adds a stress concentration assuming a perfectly radial notch or fillet. 

        Ideally the function will not need diametrical inputs, I will fix this later - Simon
        
        Args:
            axial_pos (num): Position along the axis of the Shaft object to locate the stress concentration.
            radius (num): Radius of the stress concentration.
            initial_d (num): The diameter before the feature.
            final_d (num, optional): The diameter after the feature, if it is different. Defaults to None.
        """

        if 2 * radius > initial_d:
            raise ValueError("The assigned radius of the groove or fillet exceeds the diameter of the shaft.")
        dimensions = (initial_d, final_d if final_d != None else initial_d)
        self._stress_concentrations[axial_pos] = (radius, min(dimensions), max(dimensions))
        self._stress_factors[axial_pos] = dict()
        if sum(self.stress_state[0]) != 0: # to check for each possibility of a tensile force, bending moment, and torque
            self.set_kt_axial()
        if sum(self.stress_state[1]) != 0: # bending check
            self.set_kt_bending()
        if sum(self.stress_state[2]) != 0: # torsion check
            self.set_kt_torsion()

        # I think it would actually be beneficial to change the scope of the stress factor functions: they should ideally 
        # only be called when stress concentration is being added.

    def set_kt_axial(self):
        """Calculates the stress concentration factor due to axial loading at the location of each stress concentration, 
        using the dimensions stored in self._stress_concentrations.

        Raises:
            ValueError: Verifies that a stress concentration actually exists.
        """            
        # need to consider the effect of both bending and axial forces. How can this be achieved?
        # need to also choose centering of the stress concentration for later consideration...
        if len(self._stress_concentrations) != 0:
            for key, value in self._stress_concentrations:
                r, D = value[0:2]
                d = D - 2 * r
                if value[1] == value[2]:
                    a, b = interpolate_table_tuple_pair(kt_groove_tension, D / d)
                    self._stress_factors[key]["ktx"] = a * (r/d) ** b
                else:
                    a, b = interpolate_table_tuple_pair(kt_shoulder_fillet_tension, D / value[1])
                    self._stress_factors[key]["ktx"] = a * (r/value[2]) ** b
        else:
            raise ValueError("There are no stress concentrations that have been specified yet for which to find the " \
            "stress concentration factor.")
        # The above statement could be removed if directly implemented in add_stress_concentration()

    def set_kt_bending(self):
        """Calculates the stress concentration factor due to bending at the location of each stress concentration, 
        using the dimensions stored in self._stress_concentrations.

        Raises:
            ValueError: Verifies that a stress concentration actually exists.
        """            
        if len(self._stress_concentrations) != 0:
            for key, value in self._stress_concentrations:
                value = self._stress_concentrations[key]
                r, D = value[0:2]
                d = D - 2 * r
                if value[1] == value[2]:
                    a, b = interpolate_table_tuple_pair(kt_groove_bending, D / d)
                    self._stress_factors[key]["ktb"] = a * (r/d) ** b
                else:
                    a, b = interpolate_table_tuple_pair(kt_shoulder_fillet_bending, D / value[1])
                    self._stress_factors[key]["ktb"] = a * (r/value[2]) ** b
        else:
            raise ValueError("There are no stress concentrations that have been specified yet for which to find the " \
            "stress concentration factor.")
        # The above statement could be removed if directly implemented in add_stress_concentration()
    
    def set_kt_torsion(self):
        """Calculates the stress concentration factor due to torsion at the location of each stress concentration, 
        using the dimensions stored in self._stress_concentrations.

        Raises:
            ValueError: Verifies that a stress concentration actually exists.
        """   
        if len(self._stress_concentrations) != 0:
            for key, value in self._stress_concentrations:
                r, D = value[0:2]
                d = D - 2 * r
                if value[1] == value[2]:
                    a, b = interpolate_table_tuple_pair(kt_groove_tension, D / d)
                    self._stress_factors[key]["kts"] = a * (r/d) ** b
                else:
                    a, b = interpolate_table_tuple_pair(kt_shoulder_fillet_tension, D / value[1])
                    self._stress_factors[key]["kts"] = a * (r/value[2]) ** b
        else:
            raise ValueError("There are no stress concentrations that have been specified yet for which to find the " \
            "stress concentration factor.")
    
    def set_kf(self):
        """Calculates the fatigue stress concentration factor due to alternating stress at the location of each stress concentration, 
        using the dimensions stored in self._stress_concentrations.

        Raises:
            ValueError: Verifies that a stress concentration actually exists.
        """   
        neuber_cnst = interpolate_table_value(neuber_steel,self.Sut) # hard-coded for now
        for key, value in self._stress_concentrations:
            q = 1 / (1 + neuber_cnst / np.sqrt(value[0]))
            ktb = self._stress_factors[key]["ktb"]
            kts = self._stress_factors[key]["kts"]
            self._stress_factors[key]["kf"] = 1 + q * (ktb - 1)
            self._stress_factors[key]["kfs"] = 1 + q * (kts - 1)
    
    def set_km(self):
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

    def set_mass_of_shaft(self): # need to add the stress concentrations volume addition after
        """Calculates the mass (and thus the volume due to assumed homogeneity of the material) of the shaft.
        """        
        vol = 0
        keys = list(self.diameter.keys())
        for index in range(len(keys)):
            l = keys[index] - keys[index - 1]
            d = self.diameter[index]
            vol += 0.25 * l * np.pi * d ** 2
        self.volume = vol
        self.mass = vol * self.rho


    
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
