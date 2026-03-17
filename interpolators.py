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
    a, b = table_key
    c, d = float, float
    pinion_list, gear_list = zip(*table.keys())
    if a < pinion_list[0] or a > pinion_list[-1]:
        raise ValueError("The input number of pinion teeth" \
        "is not within the bounds of the dictionary keys, " \
        f"being {pinion_list[0]} and {pinion_list[-1]}.")
    if b < gear_list[0] or b > gear_list[-1]:
        raise ValueError("The input number of gear teeth" \
        "is not within the bounds of the dictionary keys, " \
        f"being {gear_list[0]} and {gear_list[-1]}.")
    
    xp1, xp2, fp1, fp2 = list, list, list, list

    for i in range(len(pinion_list)):
        if a >= pinion_list[i]:
            xp1 = [pinion_list[i],pinion_list[i-1]]
            fp1, fp2
        for j in range(len(gear_list)):
            if b >= gear_list[j]:
                xp2 = [gear_list[j],gear_list[j-1]]
                fp1, fp2 = [table[0][0]]

            
        
    
    
    
    return (a,b)