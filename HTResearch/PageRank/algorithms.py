#
# algorithms.py
# A module containing useful algorithms for calculating PageRank weights from a matrix.
#

# stdlib imports
from numpy import multiply
from scipy import linalg
from scipy.linalg import LinAlgError
from numpy import float64

# project imports
from HTResearch.Utilities.lists import index_of

def google_matrix(matrix):
    """
    Simulates random browsing behavior by multiply each value by a
    dampening factor and then adding adding (1 - DAMP)/(number of organizations)
    to every cell in the matrix.

    Arguments:
        matrix ([[float]]): A square, float matrix in which every row and column sum to one.
                            This object will be altered during the operation.

    Returns:
        matrix ([[float]]): The dampened, "Google" matrix.
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
    """
    Calculates the left eigenvector for a given matrix.

    Arguments: matrix ([[float]]): The dampened, "Google" matrix.

    Returns:
        left_eigenvector ([float]): A vector of weights for each site.
    """
    try:
        evals, evecs = linalg.eig(a=matrix, left=True, right=False, overwrite_a=True, check_finite=False)
    except LinAlgError as e:
        return None
    evec_ind = index_of(evals, lambda x: x > .99 and x < 1.01)
    return evecs[:,evec_ind]
