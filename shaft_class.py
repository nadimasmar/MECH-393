from tables_values import *

class Shaft():
    """By default, the shaft will be initialized as a steel shaft. These values will be input later."""
    def __init__(self, length, stresses, units="metric"):
        if units != ("metric" or "imperial"):
            raise RuntimeError('Could not create an instance of the class: incorrect standard unit system created')
        self.units = units
        self.E = None # perhaps read a dictionary of stress values to input a material
        self.nu = None
        self.material_properties = None # Should we store properties in an array or explicitly as attributes? Is it necessary or should we have global values?
        self.length = length
        self.components = dict() # should the components be the keys or the values?
        self.stress_concentrations = dict()
        self.diameter = None
        self.rotating = False
        self.ang_speed = None
        self.stress_state = stresses # This should be standardized as the stresses at x = 0 (maybe, this would zero the moment in shear moment diagram)


    def __len__(self):
        return self.length
    
    def __str__(self):
        string = ""
        string.append(f"A {self.material_properties}, {len(self)}-long shaft")
        gear_num = sum([isinstance(x,Gear) for x in self.components.keys()])
        if gear_num > 0:
            # need a way to get the positions of the gears. not necessary right now
            string.append(f" with {gear_num} gears at {self.components[2]}")

    
"""some functions could be defined:

find critical points would return positions where the moment or shear is maximum, or where there are stress concentrations
Need a method of storing stress concentration features on the shaft
determine torque transfer and resulting velocity: done through the gear ratio
critical diameter of a shaft
critical length of a key
optimal gear ratio
safety factors! Or force safety factors dependent on case (see the slides for specific cases)

elasticipy can be VERY useful (J2 for von mises, eigenstresses, tensor)
"""
# Should we define a subclass within the Shaft class as something like a ShaftAssembly? It would inherit the attributes but we could add that dictionary of components.

def effective_endurance_limit(S_ut,d_min,):
    return 0
