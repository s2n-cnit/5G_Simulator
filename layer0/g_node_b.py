"""
gNodeB class
"""
from centralized import CentralizedScheduler
from ue import Ue
from typing import List

from packet import PUSCH


class GNodeB:
    """

    Attributes
    ----------
    params : dict
        Parameters of the simulation.
    n_channels : int
        Number of orthogonal channel in the system.
    ues_list : List[Ue]
        List with the active UEs in the system.
    starting_state : int
        !TODO

    """
    def __init__(self, params: dict, n_channels: int, ues_list: List[Ue], starting_state):
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.carrier_frequency = 0  # Carrier frequency used for a transmission in a given instant
        self.scheduler = CentralizedScheduler(params, n_channels, ues_list)
        self.channel = 0  # Current channel used
        self.state = starting_state
        self.t_state = 0
        self.g_node_b_scheduling_request_periodicity = 0
        self.g_node_b_scheduling_response_periodicity = 0
        self.rx_pucch = False
        self.tx_pdcch = False
        self.back_rx_data = False
        self.retransmission = False
        self.transceiver_params = {
            "Transmit power": 30,  # dBm
            "Antenna gain": 9,  # dB
            "Noise figure": 2,  # dB # was 5
        }

    def set_coordinates(self, x_input, y_input, z_input):
        self.x = x_input
        self.y = y_input
        self.z = z_input

    def get_coordinates(self):
        return self.x, self.y, self.z

    def set_carrier_frequency(self, input_carrier_frequency: float):
        self.carrier_frequency = input_carrier_frequency   

    def get_carrier_frequency(self):
        return self.carrier_frequency   

    def get_state(self):
        return self.state
    
    def set_state(self, input_state: str):
        self.state = input_state
    
    def update_state_duration(self, input_ticks: int):
        self.t_state += input_ticks

    def get_state_duration(self):
        return self.t_state
    
    def get_scheduling_request_periodicity(self, ue: Ue):
        self.g_node_b_scheduling_request_periodicity = ue.g_node_b_get_scheduling_request_periodicity()
        return self.g_node_b_scheduling_request_periodicity
    
    def get_scheduling_response_periodicity(self, ue: Ue):
        self.g_node_b_scheduling_response_periodicity = ue.get_scheduling_response_periodicity()
        return self.g_node_b_scheduling_response_periodicity

    def assign_pucch_to_ues(self, simulator_tick_duration: float):
        ue_list_ordered = self.scheduler.assign_pucch_to_ues(simulator_tick_duration)
        return ue_list_ordered

    def generate_pdcch_list(self):
        return self.scheduler.generate_pdcch_list()

    def decode_received_puschs(self, core_network_delay: int, simulator_tick_duration: float, pusch_list: List[PUSCH],
                               is_received: List[bool]):
        return self.scheduler.decode_received_puschs(core_network_delay, simulator_tick_duration, pusch_list,
                                                     is_received)

    def set_channel(self, input_channel: int):
        self.channel = input_channel

    def get_channel(self):
        return self.channel
