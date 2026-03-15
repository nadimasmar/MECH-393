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