from shaft_tables import *
from tables_values import *
import numpy as np
from Goodman_safety_factor_calculator import *
from Fatigue_strength_calculator import *
from baseStressCalculator import *
#from beambending import beam
from interpolators import *
from keys import *
import matplotlib.pyplot as plt

''' All values in SI units (mm, N, etc.), and keys are assumed to be
rectangular parallel keys, unless otherwise specified.'''

pi = np.pi

class Shaft:
    pi = np.pi
    """By default, the shaft will be initialized as a steel shaft. These dimensions will be input later."""
    def __init__(self, length, material_name, working, diameter):
        self.material = material_name
        self.Sy, self.Sut, self.HB, self.nu, self.E, self.G, self.rho = steels[material_name][working]
        self.length = length
        self.diameter = self._configure_diameter(diameter) # a bit annoying to pronounce
        self.volume = 0
        self.mass = 0
        self._stress_concentrations = dict()
        self._stress_factors = dict()
        self._keyways = dict()
        self.rotating = False
        self.ang_speed = None
        self.point_loads = set()
        self.torque = float
        self.distributed_loads = set() # This should be standardized as the stresses at x = 0 (maybe, this would zero the 
        # moment in shear moment diagram)

    def __len__(self):
        return self.length

    def is_rotating(self,speed: float | int =0):
        self.rotating = True
        self.check_whirling(speed)
        self.ang_speed = speed

    def check_whirling(self, speed: float | int):
        """Checks if the shaft would be whirling at the nominal angular velocity.

        Args:
            speed (float,int): The speed at which the Shaft is spinning.
        """        
        if self.mass == 0:
            self.set_mass_of_shaft()
        # making a terrible lump mass approximation
        # assuming fixed-fixed connection
        weight = self.mass * 9.81
        r_squared = self.volume / self.length / pi
        I_zz = r_squared ** 2 * pi / 4
        max_delta = weight * self.length ** 3 / (192 * self.E * I_zz)
        omega_n = np.sqrt(9810 / max_delta)
        check = speed / omega_n > 0.9 and speed / omega_n < 1.1
        if check:
            print("Warning: the shaft may be whirling, which " \
            "may damage parts of the shaft.")
        else:
            print(f"The natural frequency is approximately {omega_n}")
            
    
    def _configure_diameter(self, diameter: float | int):
        """Configures the variation of diameter along the shaft into a dictionary.

        Args:
            diameter (dict or num): One or more shaft diameters, in numerical or dictionary form

        Returns:
            dict: Dictionary defining the variation in diameter of the Shaft
        """        
        if isinstance(diameter, dict):
            return diameter.update({self.length: list(diameter.values())[-1]})
        elif isinstance(diameter, (float, int)):
            return {0 : diameter, self.length : diameter}
    
    def add_stress_concentration(self, axial_pos: float, radius: float) -> None:
        """Adds a stress concentration, assuming a perfectly radial notch or fillet. 

        Args:
            axial_pos (num): Position along the axis of the Shaft object to locate the stress concentration.
            radius (num): Radius of the stress concentration.
        """
        if axial_pos > self.length or axial_pos < 0:
            raise ValueError("The axial position of the stress concentration exceeds the length of the shaft.")

        isgroove = bool
        initial_d = float
        final_d = float

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
            a, b = float, float
            if isgroove:
                a, b = interpolate_table_tuple_pair(kt_groove_tension, D / d)
            else:
                a, b = interpolate_table_tuple_pair(kt_shoulder_fillet_tension, D / d)
            factors["ktx"] = a * (r/d) ** b

        def set_kt_bending():
            """Calculates the stress concentration factor due to bending at the location of each stress concentration, 
            using the dimensions stored in self._stress_concentrations.
            """
            a, b = float, float
            if isgroove:
                a, b = interpolate_table_tuple_pair(kt_groove_bending, D / d)
            else:
                a, b = interpolate_table_tuple_pair(kt_shoulder_fillet_bending, D / d)
            factors["ktb"] = a * (r/d) ** b

        def set_kt_torsion():
            """Calculates the stress concentration factor due to torsion at the location of each stress concentration, 
            using the dimensions stored in self._stress_concentrations.
            """
            a, b = float, float
            if isgroove:
                a, b = interpolate_table_tuple_pair(kt_groove_tension, D / d)
            else:
                a, b = interpolate_table_tuple_pair(kt_shoulder_fillet_tension, D / d)
            factors["kts"] = a * (r/d) ** b

        def set_kf():
            """Calculates the fatigue stress concentration factor due to alternating stress at the location of each stress concentration, 
            using the dimensions stored in self._stress_concentrations.
            """
            neuber_cnst = interpolate_table_dimensions(neuber_steel, self.Sut * 0.14504) # hard-coded for now to convert to ksi
            q = 1 / (1 + neuber_cnst / np.sqrt(r))
            ktb = factors["ktb"]
            kts = factors["kts"]
            factors["kf"] = 1 + q * (ktb - 1)
            factors["kfs"] = 1 + q * (kts - 1)

        def set_km():
            """Calculates the fatigue stress concentration factor applied to mean stresses at the location of a stress concentration,
            using the dimensions of the concentration."""

            bending = baseStressCalculator.bending_stress(max(self.point_loads))
            torsion = baseStressCalculator.torsion_stress(self.torque, d)
            max_stress = baseStressCalculator.von_mises_equivalent(np.array[[bending, torsion, 0],[torsion, 0, 0],[0,0,0]])

            kf = factors["kf"]
            kfs = factors["kfs"]
            kfm = float
            kfsm = float

            if kf * max_stress < self.Sy:
                kfm = kf
            elif kf * 2 * max_stress < 2 * self.Sy:
                kfm = (self.Sy - kf * bending) / torsion
            else:
                kfm = 0

            if kfs * max_stress < self.Sy:
                kfsm = kfs
            elif kfs * 2 * max_stress < 2 * self.Sy:
                kfsm = (self.Sy - kfs * bending) / torsion
            else:
                kfsm = 0
            
            factors["kfm"] = kfm
            factors["kfsm"] = kfsm
        
        set_kt_axial()
        set_kt_bending()
        set_kt_torsion()
        set_kf() # Order is important
        set_km()

        self._stress_factors[axial_pos] = factors

    def add_keyseat(self, axial_pos: float):
        """Adds a keyseat to the shaft, where a key will be placed to engage with the gear.
        Imposes the ASME recommendation that r/d remains approximately 0.021.
        It is recommended that the keyseat end before the shoulder fillet on the shaft
        begins such that the stress concentrations can be considered independently.

        Args:
            axial_pos (float): Axial position along the shaft at which the keyseat is required

        Raises:
            ValueError: _description_
        """        
        # we will enforce the ASME recommencation that the ratio r/d = 0.021
        # Also assumed is that the key is engaged
        d = 0
        if axial_pos < 0 or axial_pos > list(self.diameter.keys())[-1]:
                raise ValueError("The requested axial position is beyond the length of the shaft")
        for key, value in self.diameter:
            if axial_pos > key:
                d = value
                break
        r = 0.021 * d

        w = Key.key_dimensions_from_shaft_diameter_sqr(d)

        self._keyways[axial_pos] = (w, r)

        a, b, c = kt_keyseat_bending["B"]
        ktb = a + b * (rcl(0.021) / 10) + c * (rcl(0.021) / 10) ** 2
        
        d, e, f = kt_keyseat_torsion["B"]
        kts = d + e * (rcl(0.021) / 10) + f * (rcl(0.021) / 10) ** 2

        factors = dict()
        
        factors["ktb"] = max(ktb,kt_keyseat_bending["A"])
        factors["kts"] = max(kts,kt_keyseat_torsion["A"])
        factors["ktx"] = 1 # Could interpret this later but not worried about it right now

        neuber_cnst = interpolate_table_dimensions(neuber_steel, self.Sut * 0.14504) # hard-coded for now
        q = 1 / (1 + neuber_cnst / np.sqrt(r))
        ktb = factors["ktb"]
        kts = factors["kts"]
        factors["kf"] = 1 + q * (ktb - 1)
        factors["kfs"] = 1 + q * (kts - 1)

        bending = baseStressCalculator.bending_stress(max(self.point_loads))
        torsion = baseStressCalculator.torsion_stress(self.torque, d)
        max_stress = baseStressCalculator.von_mises_equivalent(np.array[[bending, torsion, 0],[torsion, 0, 0],[0,0,0]])

        kf = factors["kf"]
        kfs = factors["kfs"]
        kfm = float
        kfsm = float

        if kf * max_stress < self.Sy:
            kfm = kf
        elif kf * 2 * max_stress < 2 * self.Sy:
            kfm = (self.Sy - kf * bending) / torsion
        else:
            kfm = 0

        if kfs * max_stress < self.Sy:
            kfsm = kfs
        elif kfs * 2 * max_stress < 2 * self.Sy:
            kfsm = (self.Sy - kfs * bending) / torsion
        else:
            kfsm = 0
        
        factors["kfm"] = kfm
        factors["kfsm"] = kfsm

        self._keyways[axial_pos] = ()
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

    def set_mass_of_shaft(self):
        """Calculates the mass (and thus the volume due to assumed homogeneity of the material) of the shaft.

        Returns: None"""
            
        vol = 0
        steps = list(self.diameter.keys())
        for index in range(len(steps)-1):
            l = steps[index+1] - steps[index]
            d = self.diameter[steps[index]]
            vol += 0.25 * l * pi * d ** 2
        for values in self._stress_concentrations.values():
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
        # arbitrary accuracy
        vol *= 1e-9
        self.volume = round(vol, 5)
        mass = vol * self.rho
        self.mass = round(mass, 5)


    def get_shear_at(self, x: float) -> float:
        """
        Calculates the internal shear force at a specific axial position x.
        """
        if x < 0 or x > self.length:
            raise ValueError("Position x is outside the shaft boundaries.")
            
        shear = 0.0
        
        # 1. Point load contributions (forces at or to the left of x)
        for axial_pos, force in self.point_loads:
            if axial_pos <= x:
                shear += force
                
        # 2. Distributed load contributions
        for start, end, mag in self.distributed_loads:
            if start < x:
                # Determine how much of the distributed load is to the left of x
                effective_end = min(x, end)
                loaded_length = effective_end - start
                shear += mag * loaded_length
                
        return shear

    def get_moment_at(self, x: float) -> float:
        """
        Calculates the internal bending moment at a specific axial position x.
        """
        if x < 0 or x > self.length:
            raise ValueError("Position x is outside the shaft boundaries.")
            
        moment = 0.0
        
        # 1. Point load moment contributions (Force * distance to x)
        for axial_pos, force in self.point_loads:
            if axial_pos <= x:
                moment += force * (x - axial_pos)
                
        # 2. Distributed load moment contributions
        for start, end, mag in self.distributed_loads:
            if start < x:
                effective_end = min(x, end)
                loaded_length = effective_end - start
                
                # Treat the truncated distributed load as a point force at its centroid
                force_resultant = mag * loaded_length
                centroid = start + (loaded_length / 2.0)
                
                # Moment is the resultant force multiplied by the lever arm to x
                moment += force_resultant * (x - centroid)
                
        return moment

    def plot_shaft_diagrams(self, num_points=1000):
        """
            Generates and displays the Shear Force and Bending Moment diagrams 
            for a given Shaft object using its internal evaluation methods.
            
            Args:
                beam (Shaft): The initialized shaft object with loaded forces.
                num_points (int): The resolution of the evaluation arrays.
        """
        # 1. Generate the array of x-coordinates
        x_vals = np.linspace(0, self.length, num_points)
        
        # 2. Calculate Shear (V) and Moment (M) at every x-coordinate
        # Using list comprehensions to call the beam's internal methods
        V_vals = np.array([self.get_shear_at(x) for x in x_vals])
        M_vals = np.array([self.get_moment_at(x) for x in x_vals])
        
        # 3. Initialize the matplotlib figure with two stacked subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
        
        # 4. Plot Shear Force Diagram (SFD)
        ax1.plot(x_vals, V_vals, color='blue', linewidth=2)
        ax1.fill_between(x_vals, V_vals, 0, color='blue', alpha=0.2)
        ax1.axhline(0, color='black', linewidth=1)
        ax1.set_ylabel('Shear Force V')
        ax1.set_title('Shear Force Diagram')
        ax1.grid(True, linestyle='--', alpha=0.7)
        
        # 5. Plot Bending Moment Diagram (BMD)
        ax2.plot(x_vals, M_vals, color='red', linewidth=2)
        ax2.fill_between(x_vals, M_vals, 0, color='red', alpha=0.2)
        ax2.axhline(0, color='black', linewidth=1)
        ax2.set_xlabel('Position x')
        ax2.set_ylabel('Bending Moment M')
        ax2.set_title('Bending Moment Diagram')
        ax2.grid(True, linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        plt.show()

    def min_diameter_equation(self, 
                              safety_factor: float, 
                              T_a: float, 
                              T_m: float, 
                              M_a: float, 
                              M_m: float, 
                              Sf: float, 
                              Sut: float
                              ):
        kf, kfs, kfm, kfsm = float, float, float, float
        if len(self._stress_factors) == 0:
            kf, kfs, kfm, kfsm = 1, 1, 1, 1
        else:
            factors = self._stress_factors.values()
            kf = max([i["kf"] for i in factors])
            kfs = max([i["kfs"] for i in factors])
            kfm = max([i["kfm"] for i in factors])
            kfsm = max([i["kfsm"] for i in factors])
        d = (32 * safety_factor / pi * (np.sqrt((kf * M_a) ** 2 + 3 / 4 * (kfs * T_a) ** 2) / Sf + \
                                np.sqrt((kfm * M_m) ** 2 + 3 / 4 * (kfsm * T_m) ** 2) / Sut)) ** (1/3)        
        return d

    def min_diameter(self, torque: float, bending_moment: float, tension: float, safety_factor: float =2.5):
        
        dimensions = {"diameter" : min(self.diameter.values())}
        Sf = FatigueStrengthCalculator.calc_corrected_fatigue_strength(
            self.Sut, "steel", "shaft", dimensions, "cold-rolled", "bending", 50, 25)
        d = self.min_diameter_equation(safety_factor,0,torque,bending_moment,tension,Sf,self.Sut)
        return d

    def safety_factor(self, Sf: float, bending_moment: float, gear_moment: float, tension: float, torque: float):

        d = min(self.diameter.values())

        weight_bending = baseStressCalculator.bending_stress(bending_moment, d)
        gear_bending = baseStressCalculator.bending_stress(gear_moment, d)
        mean_axial = baseStressCalculator.axial_stress(tension, d)
        mean_torque = baseStressCalculator.torsion_stress(torque, d)
        alt_shear = 0 # baseStressCalculator.transverse_shear(reaction_force, d) Ignore for now because negligible

        alt_tensor = np.array([[weight_bending, alt_shear, 0], [alt_shear, gear_bending, 0],[0, 0, 0]])
        mean_tensor = np.array([[mean_axial, mean_torque, 0],[mean_torque, 0, 0],[0, 0, 0]])
        alternating_stress = baseStressCalculator.von_mises_equivalent(alt_tensor)
        mean_stress = baseStressCalculator.von_mises_equivalent(mean_tensor)

        Nf = GoodmanSafetyFactorCalculator.calc_safety_factor_case_2(Sf,self.Sut,alternating_stress,mean_stress)
        return Nf
    

    def force_balance(self, 
                      bearing_pos1: float | int, 
                      bearing_pos2: float | int, 
                      gear_pos1 : float | int, 
                      gear_pos2 : float | int, 
                      radial_gear_force: float | int = 0):
        """Determines the reaction forces of the shaft at different positions. Assumes 
        that the center of gravity is at the half length of the shaft (ergo balanced around
        its half length). 

        Args:
            bearing_pos1 (num): The position of the first supporting bearing.
            bearing_pos2 (num): The position of the second supporting bearing.
            gear_pos1 (num): The position of the first assembled gear
            gear_pos2 (num): The position of the second assembled gear
            radial_gear_force (num ): The radial force applied by a gear.

        Returns:
            list: list of 3-tuples containing the forces, their positions, and 
            their axial alignments.

        MUST ACCOUNT FOR THE MASS OF SHAFT COMPONENTS.
        """

        weight, length = self.mass * 9.81, self.length
        Rb = weight * (length / 2 - bearing_pos1) / (bearing_pos2 - bearing_pos1)
        Ra = weight - Rb

        forces = [Rb, Ra, radial_gear_force, -radial_gear_force]
        position = [bearing_pos1, bearing_pos2, gear_pos1, gear_pos2]
        alignment = ["vertical", "vertical", "horizontal", "horizontal"]           

        return zip(forces, position, alignment)
    
    def shear_moment_diagram(self):
        return None




    
def iterate_diameter():
    return "something"