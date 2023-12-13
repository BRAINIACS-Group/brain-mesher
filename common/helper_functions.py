from math import ceil

def round_to_interval(value, interval):
    return interval*round(value/interval)

def value_in_square_bounds(n_coords, bounds, inside=True):
    """
    Determines in 3D coordinates are within the given square bounds

    Parameters
    ----------
    n_coords : array(float)
        3D coordinates.
    bounds : array(float)
        3D square bounds given as [xmin, xmax, ymin, ymax, zmin, zmax].
    inbounds : bool, optional
        determine is check is for inside bounds given or outside bounds given.

    Returns
    -------
    bool
        Confirmation of in bounded square or not.

    """
    if inside:
        if ( (n_coords[0] > bounds[0]) and (n_coords[0] < bounds[1]) and
                (n_coords[1] > bounds[2]) and (n_coords[1] < bounds[3]) and
                (n_coords[2] > bounds[4]) and (n_coords[2] < bounds[5]) ):
                return True
    else:
        if ( ((n_coords[0] < bounds[0]) or (n_coords[0] > bounds[1])) or
                ((n_coords[1] < bounds[2]) or (n_coords[1] > bounds[3])) or
                ((n_coords[2] < bounds[4]) or (n_coords[2] > bounds[5])) ):
                return True
    return False

def calculate_max_number(map_of_interest):
    """
    Calculates the maximum number in a map of keys with numbers

    Parameters
    ----------
    map_of_interest : map(int,array)
        Map of array with nubes (keys) and associated data (values.

    Returns
    -------
    max_node_num : int
        maximum number in keys rounded up.

    """
    max_node_num = max(list(map_of_interest.keys()))
    len_of_num = (len(str(max_node_num))-1)
    max_node_num = ceil(max_node_num/(10**len_of_num))*(10**len_of_num)
    return max_node_num

def increment_numbers(map_of_old, current_map):
    """
    Increments current numbers based on existsing map numbers

    Parameters
    ----------
    map_of_old : Map(int,array)
        Map of existsign numbers.
    current_map : Map(int,array)
        Map of new numbers.

    Returns
    -------
    replacement_Map : Map(int,array)
        Map of new incremented numbers.

    """
    startnum = calculate_max_number(current_map)
    replacement_Map = {}
    old_nums = list(map_of_old.keys())
    for n in old_nums:
        value = map_of_old.pop(n)
        value.set_number(n+startnum)
        replacement_Map[n+startnum] = value
    return replacement_Map