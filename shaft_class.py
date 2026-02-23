from tables_values import *

class Shaft():
    """By default, the shaft will be initialized as a steel shaft. These values will be input later."""
    def __init__(self, length, stresses, material):
        self.Sy, self.Sut, self.HB, self.nu, self.E, self.G, self.rho = material # perhaps read a dictionary of stress values to input a material
        # Should we store properties in an array or explicitly as attributes? Is it necessary or should we have global values?
        self.length = length
        self.components = dict() # should the components be the keys or the values?
        self.stress_concentrations = dict()
        self.ktx = None
        self.ktb = None
        self.kts = None
        self.diameter = dict()
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

    def is_rotating(self,speed=0):
        self.rotating = True
        self.ang_speed = speed
    
    def add_stress_concentration(self,axial_pos,radius,initial_d=None,final_d=None):
        """Adds a stress concentration assuming a perfectly radial notch or fillet. 

        Ideally the function will not need diametrical inputs, I will fix this later - Simon
        
        Args:
            axial_pos (num): Position along the axis of the Shaft object to locate the stress concentration.
            radius (num): Radius of the stress concentration.
            initial_d (num): The diameter before the feature.
            final_d (num, optional): The diameter after the feature, if it is different. Defaults to None.
        """
        self.stress_concentrations[axial_pos] = (radius, initial_d, final_d if final_d != None else initial_d)
        if sum(self.stress_state[0]) != 0: # to check for each possibility of a tensile force, bending moment, and torque
            self.get_kt_axial()
        if sum(self.stress_state[1]) != 0: # bending check
            self.get_kt_bending()
        if sum(self.stress_state[2]) != 0: # torsion check
            self.get_kt_torsion()

    def get_kt_axial(self):
        # need to consider the effect of both bending and axial forces. How can this be achieved?
        # need to also choose centering of the stress concentration for later consideration...
        if len(self.stress_concentrations) != 0:
            keys = self.stress_concentrations.keys()
            for pos in keys:
                vals = self.stress_concentrations[pos]
                r, D = vals[0:2]
                d = D - 2 * r
                if vals[1] == vals[2]:
                    a, b = kt_groove_tension[D / d]
                    self.ktx[pos] = a * (r/d) ** b
                else:
                    a, b = kt_shoulder_fillet_tension[D / vals[2]]
                    self.ktx[pos] = a * (r/vals[2]) ** b

    def get_kt_bending(self):
        if len(self.stress_concentrations) != 0:
            keys = self.stress_concentrations.keys()
            for pos in keys:
                vals = self.stress_concentrations[pos]
                r, D = vals[0:2]
                d = D - 2 * r
                if vals[1] == vals[2]:
                    a, b = kt_groove_bending[D / d]
                    self.ktb[pos] = a * (r/d) ** b
                else:
                    a, b = kt_shoulder_fillet_bending[D / vals[2]]
                    self.ktb[pos] = a * (r/vals[2]) ** b
    
    def get_kt_torsion(self):
        if len(self.stress_concentrations) != 0:
            keys = self.stress_concentrations.keys()
            for pos in keys:
                vals = self.stress_concentrations[pos]
                r, D = vals[0:2]
                d = D - 2 * r
                if vals[1] == vals[2]:
                    a, b = kt_groove_tension[D / d]
                    self.kts[pos] = a * (r/d) ** b
                else:
                    a, b = kt_shoulder_fillet_tension[D / vals[2]]
                    self.kts[pos] = a * (r/vals[2]) ** b

metal = steel_carbon["cold rolled"][1010]
stresses = [[0, 0, 0],[0, 10, 0],[0, 0, 0]]
length = 5
shaft = Shaft(length,stresses,metal)
print(len(shaft))
shaft.diameter = {0 : 0.3, 3 : 0.275}
print(len(shaft.stress_concentrations))
shaft.add_stress_concentration(3, 0.3, 0.275)
shaft.ktb


            








    
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
