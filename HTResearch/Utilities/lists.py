def index_of(list, find):
    """Return first item in list where find(item) == True."""
    for index, val in enumerate(list):
        if find(val):
            return index

    return -1