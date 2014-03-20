#
# lists.py
# A module containing extension methods for lists.
#


def index_of(list, find):
    """
    Returns the first index of an item satisfying a Boolean function.

    Arguments:
        list (list): The list to search.
        find (function): The function to perform on each list element.

    Returns:
        The index of the first element satisfying the expression.
    """
    for index, val in enumerate(list):
        if find(val):
            return index

    return -1