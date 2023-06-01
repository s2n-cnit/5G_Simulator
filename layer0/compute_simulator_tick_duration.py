"""
    Utility scripts to compute the duration in seconds of the simulation tick
"""
import sys


def compute_simulator_tick_duration(input_params_dict: dict):
    if 'radio' in input_params_dict:
        subcarrier_spacing = input_params_dict.get('radio').get('subcarrier_spacing')
        n_os_per_subframe = 14 * subcarrier_spacing/15  # 14 OFDM symbols per subframe and minimum subcarrier spacing of
        # 15 kHz are fixed numbers
        ofdm_symbol_duration = 1e-3 / n_os_per_subframe
        simulator_tick_duration = ofdm_symbol_duration  # FIXME: Choose how long our simulation tick should be
        return simulator_tick_duration, ofdm_symbol_duration
    else:
        sys.exit("Specify the field 'radio' in params!")
