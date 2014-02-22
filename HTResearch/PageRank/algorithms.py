from numpy import multiply
from scipy import linalg
from scipy.linalg import LinAlgError
from numpy import float64

from HTResearch.Utilities.lists import index_of

def google_matrix(matrix):
    """
    The google matrix applies a dampening factor to all nodes,
    and then adds a personalization vector to simulate
    random behavior
    """

    #CONSTANTS
    DAMP_FACTOR = 0.85

    # dampen
    matrix = multiply(matrix, DAMP_FACTOR)

    # take a column vector of ones
    # dampen with 1 - DAMP_FACTOR
    # add to every row of dampened matrix
    val = 1.0 - DAMP_FACTOR
    val *= 1.0 / len(matrix)
    vector = [val] * len(matrix)
    matrix += vector

    return matrix

def left_eigenvector(matrix):
    try:
        evals, evecs = linalg.eig(a=matrix, left=True, right=False, overwrite_a=True, check_finite=False)
    except LinAlgError as e:
        return None
    evec_ind = index_of(evals, lambda x: x > .99 and x < 1.01)
    return evecs[:,evec_ind]
