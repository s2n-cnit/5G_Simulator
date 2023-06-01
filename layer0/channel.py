import sys
import numpy as np

from math import log10
from scipy.stats import rayleigh, nakagami, rice
from scipy import constants
from ue import Ue
from g_node_b import GNodeB


class OFDMChannel:
    """
    Implementing the class describing the wireless channel.

    Attributes
    ----------
    params : dict
        Parameters of the simulation.
    n_channels : int
        Number of orthogonal channel in the system.
    factory_height : float
        Height of the factory.

    """

    def __init__(self, params, n_channels: int, factory_height: float):
        self.params = params
        self.snr_threshold_db = -5
        self.noise_temperature = 290  # Kelvin
        self.factory_height = factory_height     
        self.sigma_shadowing_dictionary = {'los': 4,  # dB
                                           'InF-SL': 5.7,
                                           'InF-DL': 7.2,
                                           'InF-SH': 5.9,
                                           'InF-DH': 4
                                           }

        # Resource blocks grid
        self.fading_grid = np.zeros((
            n_channels,
            2
        ))
        self.snr_grid = np.ones((
            n_channels,
            2
        ))
        self.sc_spacing = self.params.get('radio').get('subcarrier_spacing')
        self.carrier = self.params.get('radio').get('carrier_frequency')
        self.path_loss_exponent = self.params.get('radio').get('path_loss_exponent')
        self.fading_dictionary = {'rayleigh': rayleigh,
                                  'rician': rice,
                                  'nakagami': nakagami,
                                  }
        self.fading_rv = self.set_fading_distribution()

    def get_path_loss_from_3gpp_38901(self, tx_rx_distance: float, carrier_frequency: float, is_in_los: bool, ue: Ue,
                                      g_node_b: GNodeB):
        """
        Parameters
        ----------
        tx_rx_distance : float
            Distance between Tx and Rx, in meters.
        carrier_frequency : float
            Carrier frequency of the system, in GHz.
        is_in_los : bool
            Whether the UE is in LoS or not.
        ue : Ue
            UE considered for the communication.
        g_node_b : GNodeB
            The gNodeB considered for the communication.
        """

        # Channel model from 3GPP TR 38901
        if self.factory_height > 15:
            if g_node_b.z <= ue.z:
                channel_model = 'InF-SL'  # Indoor Factory Sparse - Low BS
            else:
                channel_model = 'InF-SH'  # Indoor Factory Sparse - High BS
        else:
            if g_node_b.z <= ue.z:
                channel_model = 'InF-DL'  # Indoor Factory Dense - Low BS
            else:
                channel_model = 'InF-DH'  # Indoor Factory Dense - High BS

        # Compute LOS path loss + shadowing
        path_loss_in_los = 31.84 + 21.50 * log10(tx_rx_distance) + 19 * log10(carrier_frequency)
        shadowing_instance_los = np.random.normal(loc=0, scale=4, size=None)

        if is_in_los:  # LOS
            path_loss = path_loss_in_los + shadowing_instance_los
        else:  # Compute NLOS path loss + shadowing
            sigma = self.sigma_shadowing_dictionary[channel_model]
            shadowing_instance_nlos = np.random.normal(loc=0, scale=sigma, size=None)
            if channel_model == "InF-SL":
                path_loss_in_nlos = 33 + 25.5 * log10(tx_rx_distance) + 20 * log10(carrier_frequency)
            elif channel_model == "InF-DL":
                path_loss_in_nlos = 18.6 + 35.7 * log10(tx_rx_distance) + 20 * log10(carrier_frequency)
            elif channel_model == "InF-SH":
                path_loss_in_nlos = 32.4 + 23 * log10(tx_rx_distance) + 20 * log10(carrier_frequency)
            else:
                path_loss_in_nlos = 33.63 + 21.9 * log10(tx_rx_distance) + 20 * log10(carrier_frequency)

            if path_loss_in_los >= path_loss_in_nlos:
                effective_path_loss = path_loss_in_los
                path_loss = effective_path_loss + shadowing_instance_los
            else:
                effective_path_loss = path_loss_in_nlos
                path_loss = effective_path_loss + shadowing_instance_nlos

        # print("Path Loss {} dB".format(path_loss))

        return path_loss

    def get_friis_path_loss_db(self, carrier_frequency: float, tx_rx_distance: float):

        # Constants
        c = constants.speed_of_light
        pi = constants.pi

        # Computation of the Friis formula
        l_0 = 20 * log10(4 * pi * carrier_frequency / c)
        l_1 = self.path_loss_exponent * 10 * log10(tx_rx_distance)
        return l_0 + l_1

    def set_fading_distribution(self):
        # !TODO Check whether we'll use it or not.
        model_params = {"scale": self.params.get('radio').get('scale')}
        fd = self.params.get('radio').get('fading_distribution')

        if fd == "nakagami":
            model_params["nu"] = self.params.get('radio').get('nu')
        if fd == "rician":
            k_linear = np.power(10, self.params.get('radio').get('k') / 10)
            model_params["b"] = np.sqrt(k_linear * 2)
            model_params["scale"] = np.sqrt(1 / (2 * (1 + k_linear)))
        if self.fading_dictionary.get(fd) is not None:
            return self.fading_dictionary.get(fd)(**model_params)
        else:
            sys.exit(("Random model " + fd + " for the fading distribution is not supported"))

    def sample_fading_rvs(self):
        self.fading_grid = self.fading_rv.rvs(self.fading_grid.shape)

    def is_received(self, ue: Ue, g_node_b: GNodeB, tx_rx_distance: float, link_direction: str):

        # Set the transmission parameters properly
        if link_direction == "uplink":
            tx = ue
            rx = g_node_b
        elif link_direction == "downlink":
            tx = g_node_b
            rx = ue
        else:
            sys.exit("The link direction is not supported")

        transmit_power = tx.transceiver_params.get('Transmit power') - 30
        transmit_gain = tx.transceiver_params.get('Antenna gain')
        receiver_gain = rx.transceiver_params.get('Antenna gain')
        carrier_frequency = tx.get_carrier_frequency()
        path_loss = self.get_path_loss_from_3gpp_38901(tx_rx_distance, carrier_frequency, ue.get_los_condition(),
                                                       ue, g_node_b)

        bandwidth = self.params.get('radio').get('bandwidth')*1e9
        noise_power = 10 * log10(constants.Boltzmann * self.noise_temperature * bandwidth)
        snr_db = transmit_power + transmit_gain + receiver_gain - path_loss - noise_power

        # if received_power >= receiver_sensitivity:
        if snr_db >= self.snr_threshold_db:
            is_received = True
        else:
            is_received = False

        return is_received, snr_db

    def get_fading_grid(self):
        return self.fading_grid

    def get_snr_grid(self):
        return self.snr_grid

    def get_capacity_grid(self):
        return self.sc_spacing * np.log2(1 + self.fading_grid * self.snr_grid)
