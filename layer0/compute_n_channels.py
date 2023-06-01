"""
    Utility scripts to compute the number of channels to be used by the gNB
"""

import math


def compute_n_channels(input_params_dict: dict):
    bandwidth = input_params_dict.get('radio').get('bandwidth') * 1e9
    if bandwidth > 400e6:
        bandwidth = 400e6
        print('WARNING: The overall bandwidth has been truncated to the maximum value of 400 MHz')

    subcarrier_spacing = input_params_dict.get('radio').get('subcarrier_spacing') * 1e3
    n_subcarriers = int(math.floor(bandwidth/subcarrier_spacing))
    n_channels = int(math.floor(n_subcarriers/12))

    # print('The number of channels that can be used is {}'.format(n_channels))

    return n_channels


