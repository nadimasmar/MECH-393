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
