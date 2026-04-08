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