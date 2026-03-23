import numpy as np

def interpolate_table_dimensions(table: dict, table_key: float):
    """Interpolates between the dimensionss stored in a dictionary, given that the dimensionss are of num type.
    Assumes the keys are increasing, such that the first key is of the lowest numerical dimensions.

    Args:
        table (dict): _description_
        table_key (float): _description_
    """
    selection = list(table.keys())
    error_message = "The input table_key is not within the bounds of the dictionary keys, being " + str(selection[0]) + "and" + str(selection[-1]) + "."
    a = float
    if table_key < selection[0] or table_key > selection[-1]:
            raise ValueError(error_message)
    for index in range(1,len(selection)):
        if table_key == selection[index]:
            a = table[selection[index]]
            break
        elif table_key < selection[index]:
            xp = [selection[index],selection[index-1]]
            fp = [table[i] for i in xp]
            a = float(np.interp(table_key,xp,fp))
            break
    return a

def interpolate_table_tuple_pair(table: dict, table_key: float):
    """Interpolates between the dimensionss stored in a dictionary, given that the dimensionss are a 2-tuple.
    Assumes the keys are decreasing, such that the first key is of highest numerical dimensions.

    Args:
        table (dict): Dictionary containing the dimensionss to be interpolated.
        table_key (float): Key, or input, for which to interpolate the dimensions.

    Returns:
        tuple: 2-tuple containing the interpolated dimensionss for the corresponding key.
    """
    selection = list(table.keys())
    error_message = f"The input table_key is not within the bounds of the dictionary keys, being {selection[0]} and {selection[-1]}."
    a, b = float(), float()
    for index in range(len(selection)):
        if table_key > selection[0] or table_key < selection[-1]:
            raise ValueError(error_message)
        elif table_key >= selection[index]:
            xp = [selection[index], selection[index-1]]
            fp1, fp2 = [table[i][0] for i in xp], [table[i][1] for i in xp]
            a, b = float(np.interp(table_key,xp,fp1)), float(np.interp(table_key,xp,fp2))
    return (a,b)

def interpolate_table_2tuple_tuple(table: dict, table_key: tuple):
    """Interpolate values from a table keyed by (pinion_teeth, gear_teeth).

    The input table is expected to map:
        (N_pinion, N_gear) -> (value_for_pinion, value_for_gear)

    This implementation performs piecewise-linear interpolation in the
    (N_pinion, N_gear) plane and supports triangular coverage (where only
    combinations with N_gear >= N_pinion are tabulated).
    """
    pinion_teeth, gear_teeth = table_key

    if gear_teeth < pinion_teeth:
        raise ValueError("Expected gear_teeth >= pinion_teeth.")

    if table_key in table:
        return table[table_key]

    pinion_values = sorted({k[0] for k in table.keys()})
    gear_values = sorted({k[1] for k in table.keys()})

    if pinion_teeth < pinion_values[0] or pinion_teeth > pinion_values[-1]:
        raise ValueError(
            "The input number of pinion teeth is not within the table bounds, "
            f"being {pinion_values[0]} and {pinion_values[-1]}."
        )
    if gear_teeth < gear_values[0] or gear_teeth > gear_values[-1]:
        raise ValueError(
            "The input number of gear teeth is not within the table bounds, "
            f"being {gear_values[0]} and {gear_values[-1]}."
        )

    def get_bounds(values, target):
        low = values[0]
        high = values[-1]
        for idx in range(1, len(values)):
            if target <= values[idx]:
                low = values[idx - 1]
                high = values[idx]
                break
        if target == values[0]:
            low = high = values[0]
        if target == values[-1]:
            low = high = values[-1]
        return low, high

    def lerp(v1, v2, t):
        return (v1[0] + t * (v2[0] - v1[0]), v1[1] + t * (v2[1] - v1[1]))

    def triangle_interp(p, g, a_xy, b_xy, c_xy, a_val, b_val, c_val):
        x1, y1 = a_xy
        x2, y2 = b_xy
        x3, y3 = c_xy

        det = (y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3)
        if det == 0:
            raise ValueError("Degenerate interpolation triangle in J_table.")

        w1 = ((y2 - y3) * (p - x3) + (x3 - x2) * (g - y3)) / det
        w2 = ((y3 - y1) * (p - x3) + (x1 - x3) * (g - y3)) / det
        w3 = 1 - w1 - w2

        return (
            w1 * a_val[0] + w2 * b_val[0] + w3 * c_val[0],
            w1 * a_val[1] + w2 * b_val[1] + w3 * c_val[1],
        )

    p_lo, p_hi = get_bounds(pinion_values, pinion_teeth)
    g_lo, g_hi = get_bounds(gear_values, gear_teeth)

    # 1D interpolation along gear direction.
    if p_lo == p_hi and g_lo != g_hi:
        v_lo = table[(p_lo, g_lo)]
        v_hi = table[(p_lo, g_hi)]
        t = (gear_teeth - g_lo) / (g_hi - g_lo)
        return lerp(v_lo, v_hi, t)

    # 1D interpolation along pinion direction.
    if g_lo == g_hi and p_lo != p_hi:
        if (p_hi, g_lo) not in table:
            raise ValueError(
                "Cannot interpolate at this point because the required table "
                f"entry ({p_hi}, {g_lo}) is missing."
            )
        v_lo = table[(p_lo, g_lo)]
        v_hi = table[(p_hi, g_lo)]
        t = (pinion_teeth - p_lo) / (p_hi - p_lo)
        return lerp(v_lo, v_hi, t)

    # Should have been caught by exact key early-return.
    if p_lo == p_hi and g_lo == g_hi:
        return table[(p_lo, g_lo)]

    a_xy = (p_lo, g_lo)
    b_xy = (p_lo, g_hi)
    c_xy = (p_hi, g_hi)
    d_xy = (p_hi, g_lo)

    if a_xy not in table or b_xy not in table or c_xy not in table:
        raise ValueError("Missing required neighbors for interpolation.")

    # If lower-right corner exists, use two-triangle interpolation in rectangle.
    # If not, interpolate in upper-left triangle (common for upper-triangular tables).
    if d_xy in table:
        # Diagonal from A -> C partitions the cell.
        cell_dx = p_hi - p_lo
        cell_dy = g_hi - g_lo
        x_frac = (pinion_teeth - p_lo) / cell_dx
        y_frac = (gear_teeth - g_lo) / cell_dy

        if y_frac >= x_frac:
            return triangle_interp(
                pinion_teeth, gear_teeth,
                a_xy, b_xy, c_xy,
                table[a_xy], table[b_xy], table[c_xy]
            )
        return triangle_interp(
            pinion_teeth, gear_teeth,
            a_xy, d_xy, c_xy,
            table[a_xy], table[d_xy], table[c_xy]
        )

    return triangle_interp(
        pinion_teeth, gear_teeth,
        a_xy, b_xy, c_xy,
        table[a_xy], table[b_xy], table[c_xy]
    )
