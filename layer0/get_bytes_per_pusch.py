"""
    Utility script to compute the number of bytes that can be transmitted in a Physical Uplink Shared Channel (PUSCH)
"""
import math


def get_bytes_per_pusch(n_subcarriers_per_pusch: int, n_os_per_pusch: int, modulation_order: int):
    """
        Return the number of bytes that can be transmitted within a PUSCH
    """
    n_bytes_per_subcarrier = math.log2(modulation_order) / 8
    n_bytes_per_pusch = n_bytes_per_subcarrier * n_subcarriers_per_pusch * n_os_per_pusch

    return n_bytes_per_pusch
