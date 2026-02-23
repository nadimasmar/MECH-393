import math
def get_face_widthFactor():
    pass
'''
externally calculated for now: velocity ratio mV, gear ratio mG, angvel, etc.
'''    

class gear:
    def __init__(self, 
                 name=None, 
                 pitch_diameter=None, num_teeth=None, pressure_angle=None,
                 circular_pitch=None, base_pitch=None, diametral_pitch=None, module=None,
                 addendum=None, dedendum=None,
                 face_width=None, quality_index=None,
                 angvel = None):
        """
        Creates a Gear instance.

        Parameters
        ----------
        name                [---]
        pitch_diameter      [m]                     diameter of equivalent rolling cylinder
        num_teeth           [dimensionless]
        pressure_angle      [degrees]               angle between line of action (slanted), and velocity (pitch circle tangent)
        circular_pitch      [m]                     distance on the pitch circle between the same point on two adjacent teeth. Equal to pitch circle circumference (pi*d), divided by the number of teeth (N)      
        base_pitch          [m^-1]                  distance between one tooth and the next, on the base circle.
        diametral_pitch     [m^-1]                  number of teeth per meter of diameter on the pitch circle. "how many teeth are laid out on an arc length equal to one pitch diameter?"
        module              []
        face_width          [m]
        addemdum            [m]     
        dedendum            [m]
        quality_index       [?]                     uh
        angvel              []
        
        Raises
        ------
        Assertion Error
            If the provided number of teeth is too low to avoid undercutting for the provided gear pressure angle
        """
        #preliminary initialization (filling known parameters)
        self.name = name
        self.pitch_diameter = pitch_diameter
        self.num_teeth = num_teeth
        self.pressure_angle = pressure_angle
        self.circular_pitch = circular_pitch
        self.base_pitch = base_pitch
        self.diametral_pitch = diametral_pitch
        self.module = module
        self.face_width = face_width      
        self.addemdum = addendum
        self.dedendum = dedendum
        self.quality_index = quality_index      
        
        #addendum based on Table 12-1: AGMA Full-Depth Gear Tooth Specs
        
    def self_autofill_values(self): 
        """
        Attempts to fill missing/unspecified attributes based on known relations between parameters. Should be run multiple times to allow filled values to propagate.
        Implemented so far:
            -> Determine pitch_diameter given (Pc,N), (Pd,N), (m,d)
            -> Determine num_teeth given (Pc,d), (Pd,d), (d,m)
            -> Determine circular_pitch given (d,N)
            -> Determine base_pitch given (Pc, phi)
            -> Determine diametral_pitch given (Pc), (m)
            -> Determine module given (d,N), (Pd)
            -> Determine addendum given (Pd)
            -> Determine dedendum given (Pd)
            -> Determine pressure_angle given (Pc, phi)
        """
        
        #attempting to autofill pitch_diameter (d)
        if self.pitch_diameter == None:
            try: self.pitch_diameter = self.circular_pitch * self.num_teeth / math.pi       #from circular pitch (Pc=pi*d/N -> d=Pc*N/pi)
            except TypeError:
                try: self.pitch_diameter = self.num_teeth / self.diametral_pitch            #from diametral pitch (Pd=N/d -> d=N/Pd)
                except TypeError:
                    try: self.pitch_diameter = self.module * self.num_teeth                 #from module (m=d/N => d=m*N)
                    except TypeError:
                        print("Unable to calculate pitch diameter!")
    
        #attempting to autofill num_teeth
        if self.num_teeth == None:
            try: self.num_teeth = math.pi * self.pitch_diameter / self.circular_pitch                       #from circular pitch (Pc=pi*d/N -> N=pi*d/Pc)
            except TypeError:
                try: self.num_teeth = self.pitch_diameter * self.diametral_pitch                            #from diametral pitch (Pd=N/d => N = Pd*d)
                except TypeError:
                    try: self.num_teeth = self.pitch_diameter / self.module                                 #from module (m=d/N => N=d/m)    
                    except TypeError:
                        print("Unable to calculate teeth number!")
        
        #attempting to autofill circular_pitch
        if self.circular_pitch == None:
            try: self.circular_pitch = (math.pi * self.pitch_diameter)/self.num_teeth                       #Pc=pi*d/N
            except TypeError:
                try: self.circular_pitch = self.base_pitch/math.cos(math.radians(self.pressure_angle))      #From base pitch (Pb=Pc*cos(phi))
                except TypeError:
                    try: self.circular_pitch = math.pi/self.diametral_pitch                                 #From diametral pitch Pd=pi/Pc
                    except TypeError:
                        print("Unable to calculate circular pitch!")
        
        #attempting to autofill base pitch
        if self.base_pitch == None:
            try: self.base_pitch = self.circular_pitch * math.cos(math.radians(self.pressure_angle))          #Pb=Pc*cos(phi)
            except TypeError:
                print("Unable to calculate base pitch!")
        
        #attempting to autofill diametral pitch
        if self.diametral_pitch == None:
            try: self.diametral_pitch = self.num_teeth/self.pitch_diameter                                  #Pd=N/d
            except TypeError:
                try: self.diametral_pitch = math.pi/self.circular_pitch                                     #from circular pitch (Pd=pi/Pc)
                except TypeError:
                    try: self.diametral_pitch = 1/self.module                                               #from module (Pd=1/m)
                    except TypeError:
                        print("Unable to calculate diametral pitch!")
                
        #attempting to autofill module
        if self.module == None:
            try: self.module = self.pitch_diameter/self.num_teeth                                           #m=d/N
            except TypeError:
                try: self.module = 1/self.diametral_pitch                                                   #m=1/Pd
                except TypeError:
                    print("Unable to calculate module!")
                
        #attempting to autofill addendum        
        if self.addemdum == None:
            try: self.module = self.addendum = 1/self.diametral_pitch                                           
            except TypeError:
                print("Unable to calculate addendum!")  

        #attempting to autofill dedendum
        if self.dedendum == None:
            try: self.module = self.dedendum = 1.25/self.diametral_pitch                                           
            except TypeError:
                print("Unable to calculate dedendum!")        
                
        #attempting to autofill pressure angle
        if self.pressure_angle == None:
            try: self.pressure_angle = math.degrees(math.acos(self.base_pitch/self.circular_pitch))         #Pb = Pc * cos(phi)
            except TypeError:
                print("Unable to autofill pressure angle! (invalid base pitch or circular pitch)")
            
        #angvel?
        
    def check_undercutting(self):
        if self.num_teeth < 2/math.sin(math.radians(self.pressure_angle)):
            print("number of teeth is under the minimum number of full-depth teeth! Undercutting will occur.")
        
    def calculate_perturbed_pressure_angle(self, pitch_radii_perturbation_percentage):
        try:
            pitch_radius = self.pitch_diameter/2
            numerator = pitch_radius*math.cos(math.radians(self.pressure_angle))
            denominator = (1+pitch_radii_perturbation_percentage/100) * pitch_radius
            return math.degrees(    math.acos(  numerator/denominator  )    )
        except TypeError:
            print("Unable to calculate perurbed pressure angle!")
                
    
    def info(self):
        for attr, value in self.__dict__.items():
            if value != None: print(f"{attr}: {value}")
        print("\n")
        
        try:
            if self.diametral_pitch < 20: print("Coarse Pitch")
            else: print("Fine Pitch")
        except: pass

    def meshwith(self, gear2):
        #self.velocityRatio(secondGear) = self.num_teeth/secondGear.num_teeth
        #self.lengthOfAction(secondGear) = self.
        self.centerDistance = self.pitch_diameter + gear2.pitch_diameter
        pass

    def Sfb(self):
        pass
    
    def Sfc(self):
        pass
    
    def perturbed_pressure_angle():
        pass
    
    @staticmethod
    def calc_bending_strength_factor(gear: "gear", pinion: "gear") -> tuple:
        # Assuming Full-Depth Teeth with HPSTC Loading

        if not isinstance(gear, gear) or not isinstance(pinion, gear):
            raise ValueError("Both gear and pinion must be instances of the Gear class.")
        
        if gear.num_teeth < pinion.num_teeth:
            raise ValueError("First input must be the gear, which has more teeth than the pinion.")
        
        if gear.pressure_angle != pinion.pressure_angle:
            raise ValueError("Both gear and pinion must have the same pressure angle.")
        
        J_table_20degrees = {
        (21, 21): (0.33, 0.33),
        (21, 26): (0.33, 0.35),
        (21, 35): (0.34, 0.37),
        (21, 55): (0.34, 0.40),
        (21, 135): (0.35, 0.43),

        (26, 26): (0.35, 0.35),
        (26, 35): (0.36, 0.38),
        (26, 55): (0.37, 0.41),
        (26, 135): (0.38, 0.44),

        (35, 35): (0.39, 0.39),
        (35, 55): (0.40, 0.42),
        (35, 135): (0.41, 0.45),

        (55, 55): (0.43, 0.43),
        (55, 135): (0.45, 0.47),

        (135, 135): (0.49, 0.49),
        }

        J_table_25degrees = {
        (14, 14): (0.33, 0.33),
        (14, 17): (0.33, 0.36),
        (14, 21): (0.33, 0.39),
        (14, 26): (0.33, 0.41),
        (14, 35): (0.34, 0.44),
        (14, 55): (0.34, 0.47),
        (14, 135): (0.35, 0.51),

        (17, 17): (0.36, 0.36),
        (17, 21): (0.36, 0.39),
        (17, 26): (0.37, 0.42),
        (17, 35): (0.37, 0.45),
        (17, 55): (0.38, 0.48),
        (17, 135): (0.38, 0.52),

        (21, 21): (0.39, 0.39),
        (21, 26): (0.40, 0.42),
        (21, 35): (0.40, 0.45),
        (21, 55): (0.41, 0.49),
        (21, 135): (0.42, 0.53),

        (26, 26): (0.43, 0.43),
        (26, 35): (0.43, 0.46),
        (26, 55): (0.44, 0.49),
        (26, 135): (0.45, 0.53),

        (35, 35): (0.46, 0.46),
        (35, 55): (0.47, 0.50),
        (35, 135): (0.48, 0.54),

        (55, 55): (0.51, 0.51),
        (55, 135): (0.53, 0.56),

        (135, 135): (0.57, 0.57),
        }

        if gear.pressure_angle == 20:
            J_table = J_table_20degrees
            vals = J_table.get((pinion.num_teeth, gear.num_teeth))
            if vals is None:
                raise ValueError("Invalid combination of teeth numbers for 20 degree pressure angle.")
            return vals
        
        elif gear.pressure_angle == 25:
            J_table = J_table_25degrees
            vals = J_table.get((pinion.num_teeth, gear.num_teeth))
            if vals is None:
                raise ValueError("Invalid combination of teeth numbers for 25 degree pressure angle.")
            return vals

def meshgears(gear1, gear2, displayInfo=False):
    gear1.meshwith(gear2)
    gear2.meshwith(gear1)
    
    if displayInfo:
        print("Gear info: \n**********")
        gear1.info()
        gear2.info()

'''
#Testing: Example 12-1 (at the end of Lecture 11)

gear1 = gear(name=None, 
             pitch_diameter=None, num_teeth=19, pressure_angle=20,
             circular_pitch=None, base_pitch=None, diametral_pitch=6, module=None,
             addendum=None, dedendum=None,
             face_width=None, quality_index=None)



for i in range(5):
    print(i)
    gear1.self_autofill_values()
    gear1.info()
'''
