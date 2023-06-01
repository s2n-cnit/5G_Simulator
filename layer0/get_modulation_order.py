"""
    Utility script to compute the M-QAM modulation order on the basis of the 3GPP SNR thresholds
"""
import sys


def get_modulation_order(scheduler_type: str, snr_db: float):
    """
        Return the number of bytes that can be transmitted within a PUSCH according to 3GPP TR 38.214
        Assumption: pusch_config = qam256 and no transform precoding
    """

    if scheduler_type == 'centralized-grant-based' or scheduler_type == 'distributed':  # Conversion of Table 5.1.3.1-2
        snr_thr1_db = 1
        snr_thr2_db = 6.9
        snr_thr3_db = 15.3
    elif scheduler_type == "centralized-semi-persistent" or\
            scheduler_type == 'centralized-grant-free':  # Conversion of Table 5.1.3.1-3
        snr_thr1_db = 1
        snr_thr2_db = 6.3
    else:
        sys.exit("Scheduler type not supported")

    if snr_db <= snr_thr1_db:  # Modulation order 2 -> QPSK, 4 -> 16QAM, 6 -> 64QAM, 8 -> 256QAM
        modulation_order = 4
    elif snr_thr1_db < snr_db <= snr_thr2_db:
        modulation_order = 16
    elif snr_thr2_db < snr_db and \
            (scheduler_type == 'centralized-semi-persistent' or scheduler_type == 'centralized-grant-free'):
        modulation_order = 64
    elif snr_thr2_db < snr_db <= snr_thr3_db:
        modulation_order = 64
    else:
        modulation_order = 256

    return modulation_order
