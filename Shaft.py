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

''' All values in SI units (mm, N, MPa etc.), and keys are assumed to be
rectangular parallel keys, unless otherwise specified.'''

pi = np.pi

class Shaft:
    pi = np.pi
    """By default, the shaft will be initialized as a steel shaft. These dimensions will be input later."""
    def __init__(self, length, diameter, material_name=4140, working="tempered 400"):
        self.material = material_name
        self.Sy, self.Sut, self.HB, self.nu, self.E, self.G, self.rho = steels[material_name][working]
        # MPa, MPa, HB, NaU, MPa, GPa, kg / m^3
        self.length = length # mm
        self.diameter = self._configure_diameter(diameter) # a bit annoying to pronounce, mm
        self.volume = 0 
        self._stress_concentrations = dict()
        self._stress_factors = dict()
        self.mass = self.set_mass_of_shaft() # kg
        self._keyways = dict() 
        self.rotating = False 
        self.ang_speed = None # rad/s
        self.point_loads_y = list() # N
        self.point_loads_z = list() # N
        self.distributed_loads_y = self.get_distributed_loads() # N/mm
        self.distributed_loads_z = list() # N/mm
        self.torque = (0, 0, 0) # N mm, positive for clockwise rotation, (start, end, mag.)

    def __len__(self):
        return self.length

    def is_rotating(self,speed: float | int =0):
        self.rotating = True
        self.check_whirling(speed)
        self.ang_speed = speed
        return None

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
        self.volume = vol
        mass = vol * self.rho * 1e-9
        self.mass = mass
        return mass

    def check_whirling(self, speed: float | int) -> bool:
        """Checks if the shaft would be whirling at the nominal angular velocity.

        Args:
            speed (num): The speed at which the Shaft is spinning.

        Returns:
            bool: True or false depending on the condition of whirling.
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
        print(f"The natural frequency is approximately {omega_n}")
        return check
            
    
    def _configure_diameter(self, diameter: dict | float | int) -> dict | float | int:
        """Configures the variation of diameter along the shaft into a dictionary.

        Args:
            diameter (dict or num): One or more shaft diameters, in numerical or dictionary form

        Returns:
            dict: Dictionary defining the variation in diameter of the Shaft
        """        
        if isinstance(diameter, dict):
            diameter[self.length] = list(diameter.values())[-1]
            return diameter
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

        if 2 * radius > initial_d: #technically wrong right now
            raise ValueError("The assigned radius of the groove or fillet exceeds the diameter of the shaft.")
        
        # Storing the stress concentration values

        diameters = (initial_d, final_d)
        r, d, D = 0, 0, 0
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
            neuber_cnst = 0
            Sut_imp = self.Sut * 0.14504
            if Sut_imp in neuber_steel.keys():
                neuber_cnst = interpolate_table_dimensions(neuber_steel, self.Sut * 0.14504) # hard-coded for now to convert to ksi
            else:
                neuber_cnst = list(neuber_steel.values())[-1] # A bit of a false cheat
            q = 1 / (1 + neuber_cnst / np.sqrt(r))
            ktb = factors["ktb"]
            kts = factors["kts"]
            factors["kf"] = 1 + q * (ktb - 1)
            factors["kfs"] = 1 + q * (kts - 1)

        def set_km():
            """Calculates the fatigue stress concentration factor applied to mean stresses at the location of a stress concentration,
            using the dimensions of the concentration."""

            bending, torsion, max_stress = self.calculate_maximum_stress_at(axial_pos)[1:4]

            kf = factors["kf"]
            kfs = factors["kfs"]
            kfm = float()
            kfsm = float()

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
        d = self.get_diameter_at(axial_pos)
        r = 0.021 * d

        w = Key.key_dimensions_from_shaft_diameter_sqr(d)[0]

        self._keyways[axial_pos] = (w, r)

        factors = dict()
        
        factors["ktb"], factors["kts"] = Key.stress_concentration_factor()
        factors["ktx"] = 1 # Could interpret this later but not worried about it right now

        neuber_cnst = 0
        Sut_imp = self.Sut * 0.14504
        if Sut_imp in neuber_steel.keys():
            neuber_cnst = interpolate_table_dimensions(neuber_steel, self.Sut * 0.14504) # hard-coded for now to convert to ksi
        else:
            neuber_cnst = list(neuber_steel.values())[-1]
        q = 1 / (1 + neuber_cnst / np.sqrt(r))
        ktb = factors["ktb"]
        kts = factors["kts"]
        factors["kf"] = 1 + q * (ktb - 1)
        factors["kfs"] = 1 + q * (kts - 1)

        bending, torsion, max_stress = self.calculate_maximum_stress_at(axial_pos)[1:4]

        kf = factors["kf"]
        kfs = factors["kfs"]
        kfm = float()
        kfsm = float()

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

        self._stress_factors[axial_pos] = factors
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

    def get_deflection_at(self, x: float | int, axis: str) -> float:
        net_deflection = 0
        I_zz = self.get_area_moment_at(x)
        if axis == 'y':
            for pos, force in self.point_loads_y:
                a, b = 0, 0
                if x > pos:
                    b = pos
                    a = self.length - pos
                else:
                    a = pos
                    b = self.length - pos
                delta = 2 * force * b ** 2 * x ** 2 \
                / (12 * self.E * I_zz * self.length ** 3) \
                * (3 * a * self.length - 3 * a * x - b * x)
                net_deflection += delta
            for start, end, mag in self.distributed_loads_y:
                net_force = (end - start) * -mag
                pos = start + (end - start) / 2
                if x > pos: 
                    b = pos
                    a = self.length - pos
                else:
                    a = pos
                    b - self.length - pos
                delta = 2 * net_force * b ** 2 * x ** 2 \
                / (12 * self.E * I_zz * self.length ** 3) \
                * (3 * a * self.length - 3 * a * x - b * x)
                net_deflection += delta
        elif axis == 'z':
            for pos, force in self.point_loads_z:
                a, b = 0, 0
                if x < pos:
                    b = pos
                    a = self.length - pos
                else:
                    a = pos
                    b = self.length - pos
                I_zz = self.get_area_moment_at(x)
                delta = 2 * force * b ** 2 * x ** 2 \
                / (12 * self.E * I_zz * self.length ** 3) \
                * (3 * a * self.length - 3 * a * x - b * x)
                net_deflection += delta
            for start, end, mag in self.distributed_loads_z:
                net_force = (end - start) * -mag
                pos = start + (end - start) / 2
                if x > pos: 
                    b = pos
                    a = self.length - pos
                else:
                    a = pos
                    b - self.length - pos
                delta = 2 * net_force * b ** 2 * x ** 2 \
                / (12 * self.E * I_zz * self.length ** 3) \
                * (3 * a * self.length - 3 * a * x - b * x)
                net_deflection += delta
        return net_deflection

    def get_diameter_at(self, x: float) -> float:
        """
        Fetches the diameter at a specific axial position x based on 
        the self.diameter dictionary.
        """
        # Sort the positions to traverse the shaft from left to right
        positions = sorted(self.diameter.keys())
        
        # Default to the first diameter
        current_d = self.diameter[positions[0]]
        
        for pos in positions:
            if x >= pos:
                current_d = self.diameter[pos]
            else:
                break
                
        return current_d
    
    def get_area_moment_at(self, x: float) -> float:
        d = self.get_diameter_at(x)
        # Assumes a cylindrical solid shaft
        I_zz = pi * d ** 4 / 64
        return I_zz

    def get_shear_at(self, x: float) -> tuple[float, float]:
        """
        Calculates the internal shear force at a specific axial position x 
        in both the Y and Z directions.
        Returns: (shear_y, shear_z)
        """
        if x < 0 or x > self.length:
            raise ValueError("Position x is outside the shaft boundaries.")
            
        shear_y = 0.0
        shear_z = 0.0
        
        # --- Y-Axis Contributions ---
        # 1. Point loads Y
        for axial_pos, force in self.point_loads_y:
            if axial_pos <= x:
                shear_y += force # N
                
        # 2. Distributed loads Y
        for start, end, mag in self.distributed_loads_y:
            if start < x:
                effective_end = min(x, end)
                loaded_length = effective_end - start
                shear_y += mag * loaded_length # N = N/mm * mm

        # --- Z-Axis Contributions ---
        # 1. Point loads Z
        for axial_pos, force in self.point_loads_z:
            if axial_pos <= x:
                shear_z += force
                
        # 2. Distributed loads Z
        for start, end, mag in self.distributed_loads_z:
            if start < x:
                effective_end = min(x, end)
                loaded_length = effective_end - start
                shear_z += mag * loaded_length
                
        return shear_y, shear_z
    
    def get_moment_at(self, x: float) -> tuple[float, float]:
        """
        Calculates the internal bending moment at a specific axial position x
        in both the Y and Z directions.
        Returns: (moment_y, moment_z)
        """
        if x < 0 or x > self.length:
            raise ValueError("Position x is outside the shaft boundaries.")
            
        moment_y = 0.0
        moment_z = 0.0
        
        # --- Y-Axis Contributions ---
        # 1. Point load moment contributions (Force * distance to x)
        for axial_pos, force in self.point_loads_y:
            if axial_pos <= x:
                moment_y += force * (x - axial_pos) #N mm = N * mm
                
        # 2. Distributed load moment contributions
        for start, end, mag in self.distributed_loads_y:
            if start < x:
                effective_end = min(x, end)
                loaded_length = effective_end - start
                
                # Treat the truncated distributed load as a point force at its centroid
                force_resultant = mag * loaded_length # N = N/mm * mm
                centroid = start + (loaded_length / 2.0)
                
                # Moment is the resultant force multiplied by the lever arm to x
                moment_y += force_resultant * (x - centroid) # Nmm = N * mm

        # --- Z-Axis Contributions ---
        # 1. Point load moment contributions (Force * distance to x)
        for axial_pos, force in self.point_loads_z:
            if axial_pos <= x:
                moment_z += force * (x - axial_pos)
                
        # 2. Distributed load moment contributions
        for start, end, mag in self.distributed_loads_z:
            if start < x:
                effective_end = min(x, end)
                loaded_length = effective_end - start
                
                # Treat the truncated distributed load as a point force at its centroid
                force_resultant = mag * loaded_length
                centroid = start + (loaded_length / 2.0)
                
                # Moment is the resultant force multiplied by the lever arm to x
                moment_z += force_resultant * (x - centroid)
                
        return moment_y, moment_z
    
    def _get_shear_mesh(self, axis, num_points=1000):
        x_vals = np.linspace(0, self.length, num_points) 
        shear = 0   
        if axis == "y":
            shear = np.array([self.get_shear_at(x)[0] for x in x_vals])
        elif axis == "z":
            shear = np.array([self.get_shear_at(x)[1] for x in x_vals])
        return shear

    def _get_moment_mesh(self, axis, num_points=1000):
        x_vals = np.linspace(0, self.length, num_points)
        moment = 0
        if axis == "y":
            moment = np.array([self.get_moment_at(x)[0] for x in x_vals])
        elif axis == "z":
            moment = np.array([self.get_moment_at(x)[1] for x in x_vals])
        return moment
    
    def calculate_nominal_stress_at(self, x: float, failure_theory="von_mises", tolerance=1e-5) -> tuple[float, float, float, float]:
        """
        Calculates the nominal stresses at a specific axial location x within a shaft.
        
        Args:
            x (float): Axial position along the shaft.
            failure_theory (str): "von_mises" or "principal".
            tolerance (float): Distance threshold to apply localized stress concentrations.
            
        Returns:
            tuple: (Resultant Moment, Bending Stress, Torsional Stress, Combined Max Stress)
        """
        if x < 0 or x > self.length:
            raise ValueError("Position x is outside the shaft boundaries.")

        # 1. Geometry and Loads
        d = self.get_diameter_at(x)
        my, mz = self.get_moment_at(x)
        m_res = np.sqrt(my**2 + mz**2) # N mm
        
        # 2. Nominal Stresses
        sigma_x_nom = baseStressCalculator.bending_stress(m_res, d) # MPa
        #(32 * m_res) / (np.pi * d**3)
        tau_nom = 0
        start, end, mag = self.torque
        if start <= x <= end:
            tau_nom = baseStressCalculator.torsion_stress(mag, d)# MPa
        # (16 * self.torque) / (np.pi * d**3)
        
        # 5. Combined Stress Theory
        if failure_theory == "von_mises":
            sigma_max = np.sqrt(sigma_x_nom**2 + 3 * tau_nom**2)
        elif failure_theory == "principal":
            sigma_max = (sigma_x_nom / 2) + np.sqrt((sigma_x_nom / 2)**2 + tau_nom**2)
        else:
            raise ValueError("failure_theory must be 'von_mises' or 'principal'")
        return m_res, sigma_x_nom, tau_nom, sigma_max

    def calculate_maximum_stress_at(self, x: float, failure_theory="von_mises", tolerance=1e-5) -> tuple[float, float, float, float]:
        """
        Calculates the internal stresses at a specific axial location x.
        
        Args:
            x (float): Axial position along the shaft.
            failure_theory (str): "von_mises" or "principal".
            tolerance (float): Distance threshold to apply localized stress concentrations.
            
        Returns:
            tuple: (Resultant Moment, Bending Stress, Torsional Stress, Combined Max Stress)
        """
        m_res, sigma_x_nom, tau_nom = self.calculate_nominal_stress_at(x)[0:3]
        
        # 3. Apply Stress Concentrations (Kt)
        kt_bending = 1.0
        kt_torsion = 1.0
        for loc, factors in self._stress_factors.items():
            if abs(x - loc) <= tolerance:
                kt_bending = max(kt_bending, factors.get("kf", 1.0))
                kt_torsion = max(kt_torsion, factors.get("kts", 1.0))
                
        # 4. Localized Stresses
        sigma_x = sigma_x_nom * kt_bending
        tau = tau_nom * kt_torsion
        
        # 5. Combined Stress Theory
        if failure_theory == "von_mises":
            sigma_max = np.sqrt(sigma_x**2 + 3 * tau**2)
        elif failure_theory == "principal":
            sigma_max = (sigma_x / 2) + np.sqrt((sigma_x / 2)**2 + tau**2)
        else:
            raise ValueError("failure_theory must be 'von_mises' or 'principal'")
            
        return m_res, sigma_x, tau, sigma_max # Nmm, rest in MPa

    def plot_maximum_stress_diagrams(self, maximum: bool, num_points: float | int =1001, failure_theory: str ="von_mises"):
        """
        Generates and displays the Resultant Bending Moment, Component Stresses, 
        and Max Stress diagrams for the shaft.
        """

        if not isinstance(maximum, bool):
            raise TypeError("The input <maximum> should be of type bool")
        # 1. Generate coordinates and dynamic tolerance for step-matching
        x_vals = np.linspace(0, self.length, num_points)
        tolerance = self.length / num_points
        
        # 2. Initialize data arrays
        M_res_vals = np.zeros(num_points)
        sigma_b_vals = np.zeros(num_points)
        tau_t_vals = np.zeros(num_points)
        sigma_max_vals = np.zeros(num_points)
        
        # 3. Discretization Loop
        for i, x in enumerate(x_vals):
            m_res, sig_b, tau_t, sig_max = 0, 0, 0, 0
            if maximum:
                m_res, sig_b, tau_t, sig_max = self.calculate_maximum_stress_at(x, failure_theory, tolerance)
            else:
                m_res, sig_b, tau_t, sig_max = self.calculate_nominal_stress_at(x, failure_theory, tolerance)
            M_res_vals[i] = m_res
            sigma_b_vals[i] = sig_b
            tau_t_vals[i] = tau_t
            sigma_max_vals[i] = sig_max
            
        # 4. Find global maximums for annotation
        max_sigma = np.max(sigma_max_vals)
        max_idx = np.argmax(sigma_max_vals)
        critical_x = x_vals[max_idx]

        # 5. Plotting (3 Stacked Subplots)
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 12), sharex=True)
        
        # Plot 1: Resultant Bending Moment Diagram
        ax1.plot(x_vals, M_res_vals, color='red', linewidth=2)
        ax1.fill_between(x_vals, M_res_vals, 0, color='red', alpha=0.2)
        ax1.set_ylabel('Resultant Moment M (N mm)')
        ax1.set_title('Resultant Bending Moment Diagram')
        ax1.grid(True, linestyle='--', alpha=0.7)
        
        # Plot 2: Component Stresses (Bending & Torsion)
        ax2.plot(x_vals, sigma_b_vals, color='orange', linewidth=2, label='Bending Stress (MPa)')
        ax2.plot(x_vals, tau_t_vals, color='green', linewidth=2, label='Torsional Stress (MPa)')
        ax2.set_ylabel('Component Stress (MPa)')
        ax2.set_title('Bending & Torsional Stresses (Shows Geometry Steps)')
        ax2.legend()
        ax2.grid(True, linestyle='--', alpha=0.7)
        
        # Plot 3: Max Stress Diagram
        ax3.plot(x_vals, sigma_max_vals, color='purple', linewidth=2)
        ax3.fill_between(x_vals, sigma_max_vals, 0, color='purple', alpha=0.2)
        
        # Annotation for Maximum Stress
        ax3.plot(critical_x, max_sigma, 'ko') # Black dot at peak
        ax3.annotate(f'Max: {max_sigma:.2e}\nat x={critical_x:.3f}', 
                     xy=(critical_x, max_sigma), 
                     xytext=(critical_x + (self.length*0.05), max_sigma * 0.9),
                     arrowprops=dict(facecolor='black', shrink=0.05, width=1.5, headwidth=6))
                     
        ax3.set_xlabel('Position x')
        
        # Dynamic labels based on theory
        if failure_theory == "von_mises":
            ax3.set_ylabel("von Mises Stress σ (MPa)")
            ax3.set_title("Maximum von Mises Stress Diagram")
        else:
            ax3.set_ylabel("Principal Stress σ (MPa)")
            ax3.set_title("Maximum Principal Stress Diagram")
            
        ax3.grid(True, linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        plt.show()

    def plot_shear_bending_diagrams(self, axis, num_points=1000):
        """
            Generates and displays the Shear Force and Bending Moment diagrams 
            for a given Shaft object using its internal evaluation methods.
            
            Args:
                axis (str): The Cartesian axis, either "horizontal" or "vertical," against which to plot the diagrams
                num_points (int, optional): The resolution of the evaluation arrays. Defaults to 1000
        """
        # 1. Generate the array of x-coordinates
        x_vals = np.linspace(0, self.length, num_points)
        
        # 2. Calculate Shear (V) and Moment (M) at every x-coordinate
        # Using list comprehensions to call the beam's internal methods
        V_vals = self._get_shear_mesh(axis, num_points)
        M_vals = self._get_moment_mesh(axis, num_points)
        
        # 3. Initialize the matplotlib figure with two stacked subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
        
        # 4. Plot Shear Force Diagram (SFD)
        ax1.plot(x_vals, V_vals, color='blue', linewidth=2)
        ax1.fill_between(x_vals, V_vals, 0, color='blue', alpha=0.2)
        ax1.axhline(0, color='black', linewidth=1)
        ax1.set_ylabel('Shear Force V (N)')
        ax1.set_title('Shear Force Diagram')
        ax1.grid(True, linestyle='--', alpha=0.7)
        
        # 5. Plot Bending Moment Diagram (BMD)
        ax2.plot(x_vals, M_vals, color='red', linewidth=2)
        ax2.fill_between(x_vals, M_vals, 0, color='red', alpha=0.2)
        ax2.axhline(0, color='black', linewidth=1)
        ax2.set_xlabel('Position x')
        ax2.set_ylabel('Bending Moment M (N mm)')
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
        """_summary_

        Args:
            safety_factor (float): _description_
            T_a (float): _description_
            T_m (float): _description_
            M_a (float): _description_
            M_m (float): _description_
            Sf (float): _description_
            Sut (float): _description_

        Returns:
            _type_: _description_

        CURRENTLY INCORRECT
        """        
        kf, kfs, kfm, kfsm = 0, 0, 0, 0
        diam = list()
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
        """_summary_

        Args:
            torque (float): _description_
            bending_moment (float): _description_
            tension (float): _description_
            safety_factor (float, optional): _description_. Defaults to 2.5.

        Returns:
            _type_: _description_
        """        
        
        dimensions = {"diameter" : min(self.diameter.values())}
        Sf = FatigueStrengthCalculator.calc_corrected_fatigue_strength(
            self.Sut, "steel", "shaft", dimensions, "cold-rolled", "bending", 50, 25)
        d = self.min_diameter_equation(safety_factor,0,torque,bending_moment,tension,Sf,self.Sut)
        dimensions["diameter"] = d
        Sf = FatigueStrengthCalculator.calc_corrected_fatigue_strength(
            self.Sut, "steel", "shaft", dimensions, "cold-rolled", "bending", 50, 25)
        d = self.min_diameter_equation(safety_factor,0,torque,bending_moment,tension,Sf,self.Sut) # Too lazy to code a while loop right now
        return d

    @staticmethod
    def safety_factor(Sf: float, Sut: float, net_bending_stress: float, torsion_stress: float, kf, kfsm, kfm = 1, uniaxial_stress: float = 0):
        """Calculates the safety factor assuming a Category II fully reversed alternating stress and mean torque.

        THIS FUNCTION IGNORES TRANSVERSE SHEAR: CHECK TREE HISTORY TO FIND THE ORIGINAL DEFINITION

        Args:
            Sf (float): The fatigue strength of the material (defined at 5E8 cycles)
            bending_moment (float): The bending moment (alternating) that is acting on the beam due to its weight
            gear_moment (float): The bending moment that is acting on the beam due to the gear pressure
            tension (float): the uniaxial tension on the shaft
            torque (float): The torque that is being transferred through the shaft
            shear (float, optional): The shear force (alternating) that is placed on the shaft. Defaults to 0 for simplicity.

        Returns:
            num: The safety factor of the shaft.
        """        

        alt_stress = (kf * net_bending_stress, 0, 0, 0, 0, 0)
        mean_stress = (kfm * uniaxial_stress, 0, 0, kfsm * torsion_stress, 0, 0)
        alternating_stress = baseStressCalculator.von_mises_equivalent(*alt_stress)
        mean_stress = baseStressCalculator.von_mises_equivalent(*mean_stress)

        Nf = GoodmanSafetyFactorCalculator.calc_safety_factor_case_2(Sf,Sut,alternating_stress,mean_stress)
        return Nf
    
    def get_distributed_loads(self):
        """Defines distributed loads affecting the shaft

        Returns:
            num: a list of distributed loads in tuple form, stored as
                (start of load, end of load, magnitude of load) 
        """        
        dist_loads = list()
        positions = list()
        for pos, diameter in self.diameter.items():
            A = pi * diameter ** 2 / 4
            A /= 1e6 # convert to m^2
            dist_loads.append(self.rho * A * 9.81)
            positions.append(pos)

        out = list()
        for i in range(len(dist_loads)-1):
            out.append((positions[i], positions[i+1], -dist_loads[i] / 1e3))
        
        return out

    def point_load_balance(self, 
                      bearing_pos1: float | int, 
                      bearing_pos2: float | int, 
                      gear_pos1 : float | int, 
                      gear_pos2 : float | int, 
                      gear_mass_1: float | int,
                      gear_mass_2: float | int,
                      gear_pd_1: float | int,
                      gear_pd_2: float | int,
                      gear_phi: float | int,
                      gear_torque_in: float | int,
                      gear_torque_out: float | int,
                      shaft_mass: float | int = None
                      ):
        """Determines the reaction forces of the shaft at different positions. Ensure that
        all dimensions are taken with respect to the first bearing (including their sign). 
        Assumes that the center of gravity is at the half length of the shaft (ergo balanced 
        around its half length). 

        Args:
            bearing_pos1 (num): The position of the first supporting bearing.
            bearing_pos2 (num): The position of the second supporting bearing.
            gear_pos1 (num): The position of the first assembled gear.
            gear_pos2 (num): The position of the second assembled gear.
            gear_mass_1 (num): The mass of the first assembled gear.
            gear_mass_2 (num): The mass of the second assembled gear.
            gear_pd_1 (num): The pitch diameter of the first assembled gear.
            gear_pd_2 (num): The pitch diameter of the second assembled gear.
            gear_phi (num): The pressure angle of both of the gears.
            gear_torque_in (num): The torque applied by the input gear.
            shaft_mass (num, optional): The mass of the shaft if otherwise calculated 
            more precisely. Defaults to None.

        Returns:
            list: list of 3-tuples containing the forces, their positions, and 
            their axial alignments.

        NEED TO RESOLVE DIRECTION OF VECTORS
        """

        # Resolving gear forces and shaft weight
        # Assuming that the gear train(s) are in the x-z plane

        tangent_force_1 = gear_torque_in * 2 / gear_pd_1 # +y
        tangent_force_2 = -gear_torque_out * 2 / gear_pd_2 # conserving moment about x, -y

        radial_force1 = abs(tangent_force_1 * np.tan(np.deg2rad(gear_phi))) # +z
        radial_force2 = abs(-tangent_force_2 * np.tan(np.deg2rad(gear_phi))) # +z

        length = self.length
        S_W = -self.mass * 9.81 # -y
        if shaft_mass is not None:
            S_W = shaft_mass * 9.81 
        G_W1, G_W2 = -gear_mass_1 * 9.81, -gear_mass_2 * 9.81 # -y, -y
        
        # Y-axis reaction forces
        MGZ_1 = (G_W1 + tangent_force_1) * (gear_pos1 - bearing_pos1) # -z
        MGZ_2 = (G_W2 + tangent_force_2) * (gear_pos2 - bearing_pos1) # -z
        MS = S_W * (length / 2 - bearing_pos1) # -z
        resultant_force =  (MS + MGZ_1 + MGZ_2) / (bearing_pos2 - bearing_pos1)
        R2y = - resultant_force
        R1y = - (S_W + G_W1 + G_W2 + tangent_force_1 + tangent_force_2 + R2y)

        # X-axis reaction forces
        
        MGY_1 = radial_force1 * (gear_pos1 - bearing_pos1)
        MGY_2 = radial_force2 * (gear_pos2 - bearing_pos1)
        resultant_force = (MGY_1 + MGY_2) / (bearing_pos2 - bearing_pos1)
        R2x = - resultant_force
        R1x = - (radial_force1 + radial_force2 + R2x)

        point_forces_y = [R2y, R1y, G_W1 + tangent_force_1, G_W2 + tangent_force_2]
        point_forces_z = [R2x, R1x, radial_force1, radial_force2]
        positions_y = [bearing_pos2, bearing_pos1, gear_pos1, gear_pos2]
        positions_z = [bearing_pos2, bearing_pos1, gear_pos1, gear_pos2]

        results_y = list(zip(positions_y, point_forces_y))
        results_z = list(zip(positions_z, point_forces_z))
        self.point_loads_y, self.point_loads_z = results_y, results_z
        
    def get_min_safety_factor(self):
        """This is the culmination of everything. This function will return the smallest safety factor when checked at multiple critical points.
        The critical points that are checked are at the stress concentrations and the locations of highest bending.

        Raises:
            ValueError: Prevents use of function for shafts with no force balance yet.

        Returns:
            num: The minimum safety factor on the shaft.
        """

        if len(self.point_loads_y) == 0:
            raise ValueError("The force balance on the shaft has not yet been completed. Please use the point_load_balance function.")
        if self.torque[2] == 0:
            choice = input("There is no torque on the shaft currently. Would you like to continue? ")
            ans = ["yes", "y", "Yes", 1, "YES"]
            if choice not in ans:
                return None
        
        num_points = 10000 # hard coded by preference
        x_axis = np.linspace(0, self.length, num_points)
        # shear_mesh = self._get_shear_mesh("horizontal", num_points)

        results = [self.calculate_maximum_stress_at(x) for x in x_axis]
        bending_stress_mesh = [results[x][1] for x in range(num_points)]
        torsion_mesh =  [results[x][2] for x in range(num_points)]
        
        # Step one: determine safety factor at maximum bending force

        axial_stress = max(bending_stress_mesh)
        j = bending_stress_mesh.index(axial_stress)
        x_pos = x_axis[j]
        torsion = torsion_mesh[j]

        dimensions = {"diameter": self.get_diameter_at(x_pos)}
        Sf = FatigueStrengthCalculator.calc_corrected_fatigue_strength(
            self.Sut, "steel", "shaft", dimensions, "cold-rolled", "bending", 50, 25)
        
        Nf = self.safety_factor(Sf, self.Sut, axial_stress, torsion, 1, 1, 1)
        
        return Nf
    
    def get_phase_angle_at(self, x: float) -> float:
        """
        Calculates the torsional windup (phase angle) in radians at a specific 
        axial position 'x', relative to the start of the torque application.
        """
        start, end, torque_mag = self.torque
        
        # If no torque, or if we are looking at a point before the torque starts
        if torque_mag == 0 or x <= start:
            return 0.0

        # We only calculate twist up to point x, or the end of the torque span (whichever comes first)
        effective_end = min(x, end)
        
        positions = sorted(self.diameter.keys())
        theta = 0.0

        for i in range(len(positions)):
            current_pos = positions[i]
            next_pos = positions[i+1] if i + 1 < len(positions) else self.length

            # Determine the overlap between this constant-diameter section and our effective span
            overlap_start = max(start, current_pos)
            overlap_end = min(effective_end, next_pos)

            if overlap_start < overlap_end:
                L_section = overlap_end - overlap_start
                d = self.diameter[current_pos]
                
                J = (self.pi * d**4) / 32
                G_MPa = self.G * 1000 
                
                theta += (torque_mag * L_section) / (J * G_MPa)

        return theta

    def check_torsional_deflection_limits(self, max_allowed_degrees: float, num_points: int = 1000) -> bool:
        """
        Sweeps the shaft to check if the torsional deflection at ANY point 
        exceeds the maximum allowable limit.
        """
        x_vals = np.linspace(0, self.length, num_points)
        
        for x in x_vals:
            twist_rad = self.get_phase_angle_at(x)
            twist_deg = np.rad2deg(twist_rad)
            
            # Use absolute values to handle negative torque directions
            if abs(twist_deg) > abs(max_allowed_degrees):
                print(f"FAILED: Deflection limit exceeded at x = {x:.3f} mm.")
                print(f"Twist is {twist_deg:.4f}°, exceeding the {max_allowed_degrees}° limit.")
                return False
                
        print(f"PASSED: All positions are within the {max_allowed_degrees}° torsional deflection limit.")
        return True