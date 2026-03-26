gear_quality = {
    # Qv, which can determine many gear stress correcting constants.
    # From tables 12-6 and 12-7 in the textbook. Keys are applications or pitch line velocities, values are tuples defining ranges of Qv.
    "cement mixer" : (3,5),
    "cement kiln" : (5,6),
    "steel mill drive" : (5,6),
    "crane" : (5,7),
    "punch press" : (5,7),
    "conveyor" : (5,7),
    "packager" : (6,8),
    "power drill" : (7,9),
    "washing machine" : (8,10),
    "printing press" : (9,11),
    "automotive" : (10,11),
    "marine" : (10,12),
    "aircraft" : (10,13),
    "gyroscope" : (12,14),

    0    : (6,8),
    800  : (8,10),
    2000 : (10,12),
    4000 : (12,14)
}

face_factor = {
    # Determined by the dimensions of the face. Key is [<gear width>]
    50  : 1.6,
    150 : 1.7,
    250 : 1.8,
    500 : 2.0
}

J_table = {
    # J-Values are stored in the following format:
    # Keys are (number of pinion teeth, number of gear teeth)
    # Values are (J of pinion, J of gear)
    20 : {
        "full depth" : {
            "tip loading" : {
                (21, 21) : (0.24, 0.24),
                (21, 26) : (0.24, 0.25),
                (21, 35) : (0.24, 0.26),
                (21, 55) : (0.24, 0.28),
                (21, 135) : (0.24, 0.29),

                (26, 26) : (0.25, 0.25),
                (26, 35) : (0.25, 0.26),
                (26, 55) : (0.25, 0.28),
                (26, 135) : (0.25, 0.29),

                (35, 35) : (0.26, 0.26),
                (35, 55) : (0.26, 0.28),
                (35, 135) : (0.26, 0.29),

                (55, 55) : (0.28, 0.28),
                (55, 135) : (0.28, 0.29),

                (135, 135) : (0.29, 0.29)
            },
            "HPSTC" : {
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
        }
    },
    25 : {
        "full depth" : {
            "tip loading" : {
                (14, 14): (0.28, 0.28),
                (14, 17): (0.28, 0.30),
                (14, 21): (0.28, 0.31),
                (14, 26): (0.28, 0.33),
                (14, 35): (0.28, 0.34),
                (14, 55): (0.28, 0.36),
                (14, 135): (0.28, 0.38),

                (17, 17): (0.30, 0.30),
                (17, 21): (0.30, 0.31),
                (17, 26): (0.30, 0.33),
                (17, 35): (0.30, 0.34),
                (17, 55): (0.30, 0.36),
                (17, 135): (0.30, 0.38),

                (21, 21): (0.31, 0.31),
                (21, 26): (0.31, 0.33),
                (21, 35): (0.31, 0.34),
                (21, 55): (0.31, 0.36),
                (21, 135): (0.31, 0.38),

                (26, 26): (0.33, 0.33),
                (26, 35): (0.33, 0.34),
                (26, 55): (0.33, 0.36),
                (26, 135): (0.33, 0.38),

                (35, 35): (0.34, 0.34),
                (35, 55): (0.34, 0.36),
                (35, 135): (0.34, 0.38),

                (55, 55): (0.36, 0.36),
                (55, 135): (0.36, 0.38),

                (135, 135): (0.38, 0.38),
            },
            "HPSTC" : {
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
        }
    }
}

def dynamic_factor(quality: int, pitch_vel: float):
    Kv = float
    Qv = quality
    assert Qv <= 12, "Very accurate gearing is outside the scope of this project"
    if Qv <= 5:
        Kv = 50 / (50 + (200 * pitch_vel) ** 0.5)
    B = 0.25 * (12 - Qv) ** 2/3
    A = 50 + 56 * (1 - B)
    Kv = (A / (A + (200 * pitch_vel) ** 0.5 )) ** B
    return Kv

load_distribution_factor = {
    50  : 1.6,
    150 : 1.7,
    250 : 1.8,
    500 : 2.0
}

application_factor = {
    # Keys are [<input application>], then [<output application>]
    "uniform" : {
        "uniform"        : 1.00,
        "moderate shock" : 1.25,
        "heavy shock"    : 1.75
    },
    "light shock" : {
        "uniform"        : 1.25,
        "moderate shock" : 1.50,
        "heavy shock"    : 2.00
    },
    "medium shock" : {
        "uniform"        : 1.50,
        "moderate shock" : 1.75,
        "heavy shock"    : 2.25
    }
}

size_factor, idler_factor= 1, 1.42 # as specified in class

rim_thickness_factor = {
    0 : None,
    0.5 : (-2,3.4),
    1.2 : (0,1.0)
}


life_factor = {
    # In the low-cyle dictionary, hardness values are specified to allow for interpolation.
    # Output is a tuple (a,b) for the equation KL = a * N ** b
    "low-cycle" : {
        400 : (9.4518, -0.148),
        250 : (4.9404, -0.1045),
        160 : (2.3194, -0.0538)
    },
    "high-cycle" :  {
        "non-critical" : (1.3558, -0.0178),
        "critical" : (1.6831,-0.0323),
    }
}

def temperature_factor(temperature):
    return max((460 + (32 + 9 / 5 * temperature) / 620), 1)

reliability_factor = {
    90    : 0.85,
    99    : 1.00,
    99.9  : 1.25,
    99.99 : 1.50
}

surface_life_factor = {
    "low-cycle" : (2.466, -0.056),
    "low-cycle nitrided" : (1.249, -0.0138),
    "non-critical" : (1.4488, -0.023)
}

elastic_coefficient_4140 = 5.99 # NEED TO CHECK WITH PROF, UNITS ARE WRONG IN SLIDES

hardness_ratio_factor = 1 # We won't consider different materials, 
# unless we actually want to (for the sake of mass optimization)
