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

# Need to add stress concentrations due to keyways...