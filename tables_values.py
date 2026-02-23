nu_steel_alloy, E_steel_alloy, G_steel_alloy, rho_steel_alloy = 0.28, 206.8, 80.8, 7800
props = nu_steel_alloy, E_steel_alloy, G_steel_alloy, rho_steel_alloy

steel_carbon = {
    # Standard notation as (Sy, Sut, HB, ν, E, G, ρ)
    # List of different carbon steels as taken from the textbook
    1010 : {
        "cold rolled" : (303, 365, 105) + props,
        "hot rolled" : (179, 324, 95) + props
    },
    1020 : {
        "cold rolled" : (393, 469, 131) + props,
        "hot rolled" : (207, 379, 111) + props
    },
    1030 : {
        "cold rolled" : (441, 524, 149) + props,
        "hot rolled" : (259, 469, 137) + props,
        "normalized" : (345, 517, 149) + props,
        "tempered 1000" : (517, 669, 255) + props,
        "tempered 800" : (579, 731, 302) + props,
        "tempered 400" : (648, 848, 495) + props
    },
    1035 : {
        "cold rolled" : (462, 552, 163) + props,
        "hot rolled" : (276, 496, 143) + props
    },
    1040 : {
        "cold rolled" : (490, 586, 170) + props,
        "hot rolled" : (290, 524, 149) + props,
        "normalized" : (372, 593, 170) + props,
        "tempered 1200" : (434, 634, 192) + props,
        "tempered 800" : (552, 758, 241) + props,
        "tempered 400" : (593, 779, 292) + props
    },
    1045 : {
        "cold rolled" : (531, 627, 179) + props,
        "hot rolled" : (310, 565, 163) + props,
    },
    1050 : {
        "cold rolled" : (579, 689, 197) + props,
        "hot rolled" : (579, 689, 197) + props,
        "normalized" : (427, 745, 217) + props,
        "tempered 1200" : (538, 717, 235) + props,
        "tempered 800" : (793, 1089, 444) + props,
        "tempered 400" : (807, 1124, 514) + props,
    },
    1060 : {
        "hot rolled" : (372, 676, 200) + props,
        "normalized" : (421, 772, 229) + props,
        "tempered 1200" : (524, 800, 229) + props,
        "tempered 1000" : (669, 965, 277) + props,
        "tempered 800" : (765, 1076, 311) + props,
    },
    1095 : {
        "hot rolled" : (455, 827, 248) + props,
        "normalized" : (496, 1014, 13) + props,
        "tempered 1200" : (552, 896, 269) + props,
        "tempered 800" : (772, 1213, 363) + props,
        "tempered 600" : (814, 1262, 375) + props
    }
}

steel_alloy = {
    # Standard notation as (Sy, Sut, HB, ν, E, G, ρ) ; key is [<number>], and then [<working type>]
    # List of different alloy steels as taken from the textbook
    1340 : {
        "annealed" : (434, 703, 204) + props,
        "tempered" : (752, 862, 250) + props
        },
    4027 : {
        "annealed" : (324, 517, 150) + props,
        "tempered" : (779, 910, 264) + props
        },
    4130 : {
        "annealed" : (359, 558, 156) + props,
        "normalized" : (434, 669, 197) + props,
        "tempered 1200" : (703, 814, 245) + props,
        "tempered 800" : (1193, 1282, 380) + props,
        "tempered 400" : (1462, 1627, 41) + props
        },
    4140 : {
        "annealed" : (421, 655, 197) + props,
        "normalized" : (655, 1020, 302) + props,
        "tempered 1200" : (655, 758, 230) + props,
        "tempered 800" : (1138, 1248, 370) + props,
        "tempered 400" : (1641, 1772, 510) + props
        },
    4340 : {
        "tempered 1200" : (855, 965, 280) + props,
        "tempered 1000" : (1076, 1172, 360) + props,
        "tempered 800" : (1365, 1469, 430) + props,
        "tempered 600" : (1586, 1724, 486) + props
        },
    6150 : {
        "annealed" : (407, 662, 192) + props,
        "tempered" : (1020, 1082, 314) + props
        },
    8740 : {
        "annealed" : (414, 665, 190) + props,
        "tempered" : (917, 993, 288) + props
        },
}

# This is a stainless steel that is extremely strong, we could verify the comparison in density to other steels. Values taken when quenched & treated at 600F.
stainless_steel = (1896, 1965, 57) + props

kt_shoulder_fillet_tension = {
    # Key is [D/d], yields (a,b) for a * (r/d) ** b
    # Constants from tables used for approximating the stress concentration factor through a filleted corner in tension
    2.00 : (1.01470, -0.30035),
    1.50 : (0.99957, -0.28221),
    1.30 : (0.99682, -0.25751),
    1.20 : (0.96272, -0.25527),
    1.15 : (0.98084, -0.22485),
    1.10 : (0.98450, -0.20818),
    1.07 : (0.98450, -0.19548),
    1.05 : (1.00480, -0.17076),
    1.02 : (1.01220, -0.12474),
    1.01 : (0.98413, -0.10474),
}

kt_shoulder_fillet_bending = {
    # Key is [D/d], yields (a,b) for a * (r/d) ** b
    # Constants from tables used for approximating the stress concentration factor through a filleted corner under a bending moment
    6.00 : (0.87868, -0.33243),
    3.00 : (0.89334, -0.30860),
    2.00 : (0.90879, -0.28598),
    1.50 : (0.93836, -0.25759),
    1.20 : (0.97098, -0.21796),
    1.10 : (0.95120, -0.23757),
    1.07 : (0.97527, -0.20958),
    1.05 : (0.98137, -0.19653),
    1.03 : (0.98061, -0.18381),
    1.02 : (0.96048, -0.17711),
    1.01 : (0.91938, -0.17032)
}

kt_shoulder_fillet_torsion = {
    # Key is [D/d], yields (a,b) for a * (r/d) ** b
    # Constants from tables used for approximating the stress concentration factor through a filleted corner under an axial torque
    2.00 : (0.86331, -0.23865),
    1.33 : (0.84897, -0.23161),
    1.20 : (0.83425, -0.21649),
    1.09 : (0.90337, -0.12692)
}

kt_groove_tension = {
    # Key is [D/d], yields (a,b) for a * (r/d) ** b
    # Constants from tables used for approximating the stress concentration factor through a groove under tension
    "inf" : (0.99372, -0.39352),
    2.00 : (0.99383, -0.38231),
    1.50 : (0.99808, -0.36955),
    1.30 : (1.00490, -0.35545),
    1.20 : (1.01070, -0.33765),
    1.15 : (1.02630, -0.31673),
    1.10 : (1.02720, -0.29484),
    1.07 : (1.02380, -0.27618),
    1.05 : (1.02720, -0.25256),
    1.03 : (1.03670, -0.21603),
    1.02 : (1.03790, -0.18755),
    1.01 : (1.00030, -0.15609)
}

kt_groove_bending = {
    # Key is [D/d], yields (a,b) for a * (r/d) ** b
    # Constants from tables used for approximating the stress concentration factor through a groove under a bending moment
    "inf" : (0.94801, -0.33302),
    2.00 : (0.93619, -0.33066),
    1.50 : (0.93894, -0.32380),
    1.30 : (0.94299, -0.31504),
    1.20 : (0.94681, -0.30582),
    1.15 : (0.95311, -0.29739),
    1.12 : (0.95573, -0.28886),
    1.10 : (0.95454, -0.28268),
    1.07 : (0.96774, -0.26452),
    1.05 : (0.98755, -0.24134),
    1.03 : (0.99033, -0.21517),
    1.02 : (0.97753, -0.19793),
    1.01 : (0.99393, -0.15238)
}

kt_groove_torsion = {
    # Key is [D/d], yields (a,b) for a * (r/d) ** b
    # Constants from tables used for approximating the stress concentration factor through a groove under an axial torque
    "inf" : (0.88126, -0.25204),
    2.00 : (0.89035, -0.24075),
    1.30 : (0.89460, -0.23267),
    1.20 : (0.90182, -0.22334),
    1.10 : (0.92311, -0.19740),
    1.05 : (0.93853, -0.16941),
    1.02 : (0.96877, -0.12605),
    1.01 : (0.97245, -0.10162)
}

neuber_steel = {
    # Dictionary of neuber constants for steels. Key is [<Sut, in kpsi>], value is sqrt(a)
    50  : 0.130,
    55  : 0.118,
    60  : 0.108,
    70  : 0.093,
    80  : 0.080,
    90  : 0.070,
    100 : 0.062,
    110 : 0.055,
    120 : 0.049,
    130 : 0.044,
    140 : 0.039,
    160 : 0.031,
    180 : 0.024,
    200 : 0.018,
    220 : 0.013,
    240 : 0.009
}

neuber_ann_al = {
    # Dictionary of Neuber constants for annealed aluminum. Key is [<Sut, in kpsi>], value is sqrt(a)
    10 : 0.500,
    15 : 0.341,
    20 : 0.264,
    25 : 0.217,
    30 : 0.180,
    35 : 0.152,
    40 : 0.126,
    45 : 0.111
}

neuber_hard_al = {
    # Dictionary of Neuber constants for work-hardened aluminum. Key is [<Sut, in kpsi>], value is sqrt(a)
    15 : 0.475,
    20 : 0.380,
    30 : 0.278,
    40 : 0.219,
    50 : 0.186,
    60 : 0.162,
    70 : 0.144,
    80 : 0.131,
    90 : 0.122
}

marin_reliability = {
    # Constants defining C_reliab, or the reliability factor in the corrected endurance limit. Key is [<% reliability>]
    50      : 1,
    90      : 0.897,
    95      : 0.868,
    99      : 0.814,
    99.9    : 0.753,
    99.99   : 0.702,
    99.999  : 0.659,
    99.9999 : 0.620
}

marin_surface_metric = {
    # Functions definining the C_surf, or surface factor in the corrected endurance limit.
    # Key is [<surface finish>], values are (a,b) for the equation a * Sut ** b
    "ground" : (1.58, -0.085),
    "machined" : (4.51, -0.265),
    "cold-rolled" : (4.51, -0.265),
    "hot-rolled" : (57.7, -0.718),
    "as-forged" : (272, -0.995)
}

marin_surface_imperial = {
    "ground" : (1.34, -0.085),
    "machined" : (2.7, -0.265),
    "cold-rolled" : (2.7, -0.265),
    "hot-rolled" : (14.4, -0.718),
    "as-forged" : (39.9, -0.995)
}

std_square_key_w_range_inch = {
    0.312 : 0.093,
    0.437 : 0.125,
    0.562 : 0.187,
    0.875 : 0.250,
    1.250 : 0.312,
    1.275 : 0.375,
    1.750 : 0.500,
    2.250 : 0.625,
    2.750 : 0.750,
    3.250 : 0.875,
    3.750 : 1.000,
    4.500 : 1.250,
    5.500 : 1.500,
}

std_rect_key_range_inch = {
    0.312 : (0.093, 0.093),
    0.437 : (0.125, 0.093),
    0.562 : (0.187, 0.125),
    0.875 : (0.250, 0.187),
    1.250 : (0.312, 0.250),
    1.275 : (0.375, 0.250),
    1.750 : (0.500, 0.375),
    2.250 : (0.625, 0.437),
    2.750 : (0.750, 0.500),
    3.250 : (0.875, 0.625),
    3.750 : (1.000, 0.750),
    4.500 : (1.250, 0.875),
    5.500 : (1.500, 1.000),
}
# https://www.engineersedge.com/gears/shaft_diameter_vs_key_sizes_14411.htm

std_square_key_range_mm = {
    # Standard cross-sectional dimensions for a square key. Key is [<diameter>], value is width or height of key.
    6   : 2,
    8   : 3,
    10  : 4,
    12  : 5,
    17  : 6,
    22  : 8,
    30  : 10,
    38  : 12,
    44  : 14,
    50  : 16,
    58  : 18,
    65  : 20,
    75  : 22,
    85  : 25,
    95  : 28,
    110 : 32,
    130 : 36,
    150 : 40,
    170 : 45,
    200 : 50,
    230 : 56,
    260 : 63,
    290 : 70,
    330 : 80,
    380 : 90,
    440 : 100
}

std_rect_key_range_mm = {
    # Standard cross sectional dimensions for a rectangular key. Key is [<diameter>], value is (width, height) of the key
    6   : (2, 2),
    8   : (3, 3),
    10  : (4, 4),
    12  : (5, 5),
    17  : (6, 6),
    22  : (8, 7),
    30  : (10, 8),
    38  : (12, 8),
    44  : (14, 9),
    50  : (16, 10),
    58  : (18, 11),
    65  : (20, 12),
    75  : (22, 14),
    85  : (25, 14),
    95  : (28, 16),
    110 : (32, 18),
    130 : (36, 20),
    150 : (40, 22),
    170 : (45, 25),
    200 : (50, 28),
    230 : (56, 32),
    260 : (63, 32),
    290 : (70, 36),
    330 : (80, 40),
    380 : (90, 45),
    440 : (100, 50)
}

'''
std_wdrf_key_inch = {
    202 : ()
}
# to do later
'''

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

size_factor = 1 # as specified in class

rim_thickness_factor = {
    0 : None,
    0.5 : (-2,3.4),
    1.2 : (0,1.0)
}

life_factor = {
    # need to figure this out later
}

reliability_factor = {
    90    : 0.85,
    99    : 1.00,
    99.9  : 1.25,
    99.99 : 1.50
}
