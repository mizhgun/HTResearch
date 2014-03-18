#
# lists.py
# A module containing extension methods for lists.
#


def index_of(list, find):
    """
    Returns the first index of an item satisfying a Boolean function.

    list - The list to search.
    find - The function to perform on each list element.
    """
    for index, val in enumerate(list):
        if find(val):
            return index

    return -1