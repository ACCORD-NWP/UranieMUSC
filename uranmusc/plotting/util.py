import numpy as np


def get_uraniters(trajnum, paranum):
    """
    parse URANIE iterations r*(k+1)

    Args:
        trajectory number
        parameter number
    """

    _iters = trajnum * (paranum + 1)
    iters = np.arange(1, _iters + 1)

    iters_list = [f"{i}" for i in iters]

    return iters_list
