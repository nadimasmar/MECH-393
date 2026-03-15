from interpolators import *

typical_friction_coeff = {
    "ball" : {
        "aligning" : 0.0010,
        "thrust" : 0.0013,
        "deep-groove" : 0.0015
    },
    "roller" : {
        "cylinder" : 0.0011,
        "spherical" : 0.0018,
        "tapered" : 0.0018,
        "needle" : 0.0045
    }
}

bearing_reliability = {
    50 : 5.0,
    90 : 1.0,
    95 : 0.62,
    96 : 0.53,
    97 : 0.44,
    98 : 0.33,
    99 : 0.21
}

class Bearing:

    def __init__(self, kind: str, reliab: float | int, axial_f: float | int, reaction_x: float| int, reaction_y: float | int, L_D: int):
        for element in [reliab, axial_f, reaction_x, reaction_y]:        
            if not isinstance(element, (float, int)):
                raise TypeError("The bearing should be initialized with the reliability" \
                "and forces as numbers.")
        self.kind = kind
        self.fortnite = 2
        self.F_a = axial_f
        self.F_r = self.resultant_force(reaction_x, reaction_y)
        self.K_r = interpolate_table_dimensions(
            bearing_reliability, 
            reliab
            )
        self.L_D = L_D
        self.C = None
        self.C0 = None
        self.X = None
        self.Y = None
        self.V = None        

    @staticmethod
    def resultant_force(reaction_x: float | int, reaction_y: float | int):
        return (reaction_x ** 2 + reaction_y ** 2) ** 0.5

    def calculate_Fa_C0(self):
        return 5 * self.F_a / (6 * self.F_r) * (self.L_D / self.K_r) ** (-1/3)

    def minimum_basic_load(self):
        """Meant to be a more interactive iterative process.

        Returns:
            _type_: _description_
        """        """"""

        i = 0
        loop = "Yes"
        base_load, C0 = float,float
        Fa_C0 = float
        equiv_P = float

        while loop == "Yes":
            if self.F_a == 0:
                equiv_P = self.F_r
            else:
                if self.C is None:
                    Fa_C0 = self.calculate_Fa_C0()
                print(f"The ratio of axial force to C0 is {round(Fa_C0,3)}. Please use " \
                    "this for the following required inputs.")
                e = float(input("Value of e for this ratio: "))
                V = float(input("Please input an expected value of V: "))
                X, Y = float, float
                if e >= self.F_a / (V * self.F_r): 
                    X, Y = 1, 0
                else:
                    print("The value of e is less than the ratio of axial to radial forces.")
                    X = float(input("Please input a value of X: "))
                    Y = float(input("Please input a value of Y: "))
                self.X, self.Y, self.V = X, Y, V
                equiv_P = X * V * self.F_r + Y * self.F_a
            
            base_load = equiv_P * (self.L_D / self.K_r) ** (1/3)
            self.C = base_load
            print("The minimum basic load rating base_load for this bearing must be " \
                f"greater than {base_load}")
            # test for a possible improvement.
            C0_new = float(input("C0 value for chosen bearing: "))
            test = self.F_a / C0_new
            if C0 != C0_new:
                answer = None
                Fa_C0 = test
                C0 = C0_new
                while answer is None:
                    answer = input("An improvement could be made to the estimation " \
                    "of the load rating and bore of the bearing. Enter 'Yes' to " \
                    "continue, and 'No' to exit: ")
                    if answer not in ["Yes", "No"]:
                        answer = None
                        print("Incorrect input. Please try again:")
                loop = answer
            else:
                loop = None
        
        self.C, self.C0 = base_load, C0
        string = f"The bearing must be rated for {base_load} N of force over one million cycles, while the limit on static loading is {C0}"
        print(string)
        return base_load

