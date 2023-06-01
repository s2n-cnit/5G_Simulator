import sys
import copy as cp
import operator
import random
import pandas as pd
from traffic_model import TrafficModel
from ue_buffer import UeBuffer
from packet import Packet, PUCCH, PDCCH, PUSCH, HARQ
from typing import List

''' 
Ue class
'''


class Ue(TrafficModel):
    def __init__(self, params, ue_id, traffic_type, starting_state):
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.params = params
        self.n_os_pusch = params.get('radio').get('n_os_pusch')
        self.ue_id = ue_id
        self.ul_buffer = UeBuffer()
        self.packet = Packet()  # Packet that is appended in the queue with periodicity equal to t_generation
        self.state = starting_state
        self.vectState = starting_state
        self.burst_size = 0  # Number of packets which form the burst
        self.traffic_type = traffic_type
        self.t_generation = random.randint(0, 56)  # Avoid to have UEs which transmit periodically aligned in time
        # self.t_generation = 28 # Avoid to have UEs which transmit periodically aligned in time
        self.scheduling_request_periodicity = 0  # Number of ticks between consecutive scheduling request occasion
        self.g_NB_scheduling_request_periodicity = 0 
        self.scheduling_request_carrier_frequency = 0  # Carrier frequency used
        # for the scheduling request transmission [GHz]
        self.scheduling_response_periodicity = 0  # Number of ticks between consecutive scheduling response occasion
        self.scheduling_response_carrier_frequency = 0  # Carrier frequency used for
        # the scheduling request transmission [GHz]
        self.scheduling_request_channel = 0  # Channel used for the scheduling request transmission
        self.scheduling_response_channel = 0  # Channel used for the scheduling request transmission
        self.initial_offset_pucch_transmission_ticks = 0
        self.initial_offset_pdcch_transmission_ticks = 0
        self.n_pucch = 2  # FIXME: Integer multiple of pucchs forming the upper bound for aperiodic traffic generation
        self.t_state = 0
        self.carrier_frequency = 50  # Current carrier frequency [GHz]
        self.channel = 0  # Current channel used
        self.distance_from_g_node_b = 0
        self.tx_pucch_with_success = False
        self.tx_pucch = False
        self.rx_pdcch = False
        self.data_is_received = False
        self.latency = 0
        self.ue_cycle = 0
        self.transmission_number = 0
        self.pucch = 0
        self.generation_time = 0
        self.arrival_time = 0
        self.n_generated_packets = 0
        self.n_discarded_packets = 0
        self.bytes_per_pusch = 0
        self.pusch_su_index = list()
        self.n_rbs_per_pusch_su = list()
        self.pusch_rb_index = list()
        self.pdcch = pd.DataFrame(columns=['UE_ID', 'Packet_ID', 'Ticks_to_wait', 'Channel'])
        self.harq = pd.DataFrame(columns=["UE_ID", "Packet_ID", "Positive", "Retransmit", "Ticks_to_wait"])
       
        self.is_in_los = False
        super(Ue, self).__init__()

        self.traffic_model = {
            "Periodic": super().get_time_periodicity,
            "Aperiodic": super().get_variable_time_periodicity,
            "Burst Periodic": super().get_time_periodicity,
            "Burst Aperiodic": super().get_variable_time_periodicity
        }

        self.transceiver_params = {
            # "Transmit power": 23,  # dBm
            "Transmit power": 10,  # dBm
            "Antenna gain": 3,  # dB
            "Noise figure": 7,  # dB
        }

    def add_new_packet(self, current_tick: int):
        """
            Add a new packet in the queue and compute the next generation instant, if the buffer is not full.
            Otherwise, just discard the packet.
        """
        new_packet = cp.copy(self.packet)
        new_packet.set_generation_time(current_tick)
        self.n_generated_packets += 1

        # Check if successfully added to the ul buffer
        if not(self.ul_buffer.add_packet(new_packet)):
            self.n_discarded_packets += 1

        if self.traffic_type in self.traffic_model:  # To avoid errors in the UE initialization
            self.t_generation += self.traffic_model[self.traffic_type]()
            self.packet.set_generation_time(self.t_generation)
        else:
            sys.exit('Traffic model ' + str(self.traffic_type) + ' not supported')

        self.packet.set_id(self.packet.get_id() + 1)

    def check_scheduling_request_need(self, priority_metric=None):

        if self.ul_buffer.get_n_packets() > 0:
            self.set_carrier_frequency(self.scheduling_request_carrier_frequency)
            self.set_channel(self.scheduling_request_channel)

            # Order packets by priority and qos_latency requirement (with higher priority for retransmissions)
            # to choose the one that needs resources
            for index, packet in enumerate(self.ul_buffer.packet_list):
                packet.n_transmissions *= -1  # To allow an ascending order for n_transmissions field too

            if priority_metric is not None:
                self.ul_buffer.order_buffer(priority_metric)
            else:
                self.ul_buffer.packet_list = sorted(self.ul_buffer.packet_list, reverse=False,
                                                    key=operator.attrgetter('priority', 'qos_latency',
                                                                            'n_transmissions'))

            for index, packet in enumerate(self.ul_buffer.packet_list):
                packet.n_transmissions *= -1  # Restore positive values

            return True
        else:
            return False

    def generate_pucch(self, current_time, first_pusch_attempt):

        """
            Generate the pucch packet, given the queue of the current UE.

        Parameter
        --------
        current_time : int
            Current time from the beginning of the simulation in ticks, needed to compute packet elapsed time.

        first_pusch_attempt : int
            Time elapsing from the beginning of the simulation to the next first PUSCH occasion in ticks,
            needed to avoid asking for resources which will never be exploited in the future

        Return
        ------
        pucch : PUCCH
            Pucch data with the related fields.

        """

        pucch = PUCCH()
        packet_id_to_be_removed = list()
        for p in self.ul_buffer.get_packet_list():
            p.update_elapsed_time(current_time - p.get_generation_time())
            if first_pusch_attempt - p.get_generation_time() >= p.get_qos_latency():
                print('WARNING: Packet {} discarded by UE {} before sending the PUCCH because '
                      'its deadline expires'.format(p.get_id(), self.get_ue_id()))
                self.n_discarded_packets += 1
                # TODO check other possible operations to be performed
                # Save packet IDs to be removed
                packet_id_to_be_removed.append(p.get_id())
            else:
                entry = pd.DataFrame([[p.get_ue_id(), p.get_id(), p.get_priority(), p.get_mb_to_sent(),
                                       p.get_min_mb_to_send(), p.get_transmission_counter(),
                                       p.get_elapsed_time(), p.get_qos_latency()]],
                                     columns=["UE_ID", "Packet_ID", "Priority", "Payload", "Bucket_Size",
                                              "Retransmission", "Elapsed_Time", "QoS_Latency"]
                                     )

                pucch.add_queue_entry(entry)
        # Remove packets that do not meet the qos_latency requirement
        for packet_id in packet_id_to_be_removed:
            self.ul_buffer.schedule_data(packet_id=packet_id)
            self.ul_buffer.remove_data(packet_id=packet_id)
        pucch_queue_request_df = pucch.get_queue_request_df()
        if not pucch_queue_request_df.empty:
            pucch.update_request_bytes()
            return pucch
        else:
            print('WARNING: UE {} cannot generate its PUCCH because either the packet queue is empty or '
                  'all packets do not meet their qos_latency requirement'.format(self.get_ue_id()))
            return None

    def decode_hybrid_arq(self, hybrid_arq_dataframe):
        filtered_harq = hybrid_arq_dataframe[hybrid_arq_dataframe["UE_ID"] == self.get_ue_id()]

        if filtered_harq.empty:
            return None
        else:
            if filtered_harq.loc[0, "Retransmit"]:
                return filtered_harq.loc[0, "Ticks_to_wait"]
            else:
                return None  # Go to the next subframe

    def is_pdcch_for_me(self, pdcch_list: List[PDCCH]):
        """
            Checks whether there is a PDCCH intended for this UE

        Parameter
        --------
        pdcch_list : list
            List of PDCCH

        Return
        ------
        is_pdcch_for_me : bool
            True if the PDCCH has been found, false otherwise

        su_index: list of tuples
            The indexes of the scheduling unit in which the UE can transmit its PUSCH

        n_rbs_per_su: list of tuples
            Number of resource blocks assigned for the transmission of the PUSCH

        rb_index: list of tuples
            The indexes of the resource blocks assigned for the transmission of the PUSCH
        """

        is_pdcch_for_me = False
        bytes_per_pusch = None
        su_index = None
        n_rbs_per_su = None
        rb_index = None
        for index, pdcch in enumerate(pdcch_list):
            if pdcch.get_ue_id() == self.get_ue_id():
                is_pdcch_for_me = True
                bytes_per_pusch = pdcch.scheduling_info_dict.get('bytes_per_pusch')
                su_index = pdcch.scheduling_info_dict.get('su_index')
                n_rbs_per_su = pdcch.scheduling_info_dict.get('n_rbs_per_su')
                rb_index = pdcch.scheduling_info_dict.get('rb_index')

        # Save the bytes that will be mapped to each PUSCH for the current group of 56 OFDM symbols
        self.bytes_per_pusch = bytes_per_pusch

        # Save the scheduling unit and channel indexes that will be used for PUSCH transmission
        self.pusch_su_index = su_index
        self.n_rbs_per_pusch_su = n_rbs_per_su
        self.pusch_rb_index = rb_index

        return is_pdcch_for_me, su_index

    def schedule_packet(self, packet_id):
        self.ul_buffer.schedule_data(packet_id=packet_id)

    def remove_packet(self, packet_id: int):  
        self.ul_buffer.remove_data(packet_id)

    def set_coordinates(self, x_input, y_input, z_input):
        self.x = x_input
        self.y = y_input
        self.z = z_input

    def get_coordinates(self):
        return self.x, self.y, self.z
    
    def get_next_packet_generation_instant(self):
        return self.t_generation

    def get_state(self):
        return self.state
    
    def set_state(self, input_state: str):
        self.state = input_state
    
    def update_state_duration(self, input_ticks: int):
        self.t_state += input_ticks

    def get_state_duration(self):
        return self.t_state

    def set_burst_size(self, burst_size):
        self.burst_size = burst_size

    def get_burst_size(self):
        return self.burst_size

    def get_ue_id(self):
        return self.ue_id

    def set_ue_id(self, ue_id):
        self.ue_id = ue_id

    def set_mb_to_be_sent(self, input_mb_to_be_sent: int):
        self.packet.mb_to_sent = input_mb_to_be_sent

    def set_min_mb_to_be_send(self, input_min_mb_to_be_send: int):
        self.packet.set_min_mb_to_send(input_min_mb_to_be_send)

    def set_new_packet_priority(self, input_priority: int):  # New packet is the one that will be appended in the queue
        # at t_generation
        self.packet.set_priority(input_priority)

    def get_new_packet_priority(self):
        return self.packet.get_priority()

    def set_new_packet_qos_latency(self, input_qos_latency: float):
        self.packet.set_qos_latency(input_qos_latency)

    def set_new_packet_qos_reliability(self, input_qos_reliability: float):
        self.packet.set_qos_reliability(input_qos_reliability)

    def set_new_packet_arrival_time(self, input_arrival_time: int): 
        self.packet.set_arrival_time(input_arrival_time)

    def set_new_packet_size(self, input_size: int):
        self.packet.set_size(input_size)

    def set_ue_id_of_new_packet(self):
        self.packet.set_ue_id(self.ue_id)

    def get_min_mb_to_be_send(self):
        return self.packet.get_min_mb_to_send()

    def get_last_packet_id(self):
        return self.packet.get_id() - 1
           
    def get_updated_packet_list(self):
        return self.ul_buffer.get_packet_list()
        
    def get_packet_list_size(self):
        return self.ul_buffer.get_n_packets()

    def set_scheduling_request_periodicity(self, scheduling_request_periodicity: int):
        self.scheduling_request_periodicity = scheduling_request_periodicity
        # Set-up the upper bound in ticks for the aperiodic traffic generation 
        # max_aperiodic_traffic_interval = self.n_pucch * scheduling_request_periodicity
        # super().set_max_generation_instant(max_aperiodic_traffic_interval)
    
    def set_scheduling_request_periodicity_g_node_b(self, scheduling_request_periodicity: int):
        self.g_NB_scheduling_request_periodicity = scheduling_request_periodicity

    def get_scheduling_request_periodicity(self):
        return self.scheduling_request_periodicity

    def g_node_b_get_scheduling_request_periodicity(self):
        return self.g_NB_scheduling_request_periodicity
    
    def get_scheduling_response_periodicity(self):
        return self.scheduling_response_periodicity

    def get_ul_buffer(self):
        return self.ul_buffer

    def set_carrier_frequency(self, input_carrier_frequency: float):
        self.carrier_frequency = input_carrier_frequency  

    def get_carrier_frequency(self):
        return self.carrier_frequency      

    def set_channel(self, input_channel: int):
        self.channel = input_channel

    def get_channel(self):
        return self.channel
    
    def get_current_packet_transmission_number(self):  # Current packet is the one that the UE is transmitting
        return self.ul_buffer.get_first_packet().get_transmission_counter()
    
    def increment_current_packet_transmission_number(self):
        self.ul_buffer.get_first_packet().increment_transmission_counter()

    def get_current_packet_priority(self):
        return self.ul_buffer.get_first_packet().get_priority()

    def get_current_packet_id(self):
        return self.ul_buffer.get_first_packet().get_id()

    def get_los_condition(self):  # NOTE: This is something the UE may not know in practise,
        # so do not use it to change its behavior during simulation
        return self.is_in_los

    def set_los_condition(self, is_in_los: bool):
        self.is_in_los = is_in_los

    def get_distance_from_g_node_b(self):  # NOTE: This is something the UE may not know in practise,
        # so do not use it to change its behavior during simulation
        return self.distance_from_g_node_b

    def set_distance_from_g_node_b(self, ue_g_node_b_distance: float):
        self.distance_from_g_node_b = ue_g_node_b_distance

    def generate_pusch(self, current_time: int, n_bytes_overhead_5g_nr: int = None):

        """
            Generate the PUSCH packet, given the queue of the current UE.

        Parameter
        --------
        current_time : int
            Current time in ticks, needed to compute packet elapsed time.

        n_bytes_overhead_5g_nr : int
            Number of bytes introduced by the 5G-NR protocol stack.
            If None, they have been already included by the UE in the previous mapping

        Return
        ------
        pucch : PUSCH
            PUSCH data with the related fields.

        """

        if self.pusch_su_index:
            pusch = PUSCH()

            # Find the number of resource blocks occupied by the PUSCH
            su_index = self.pusch_su_index[0]
            n_rb_per_su = 0
            final_index = 0
            for index, value in enumerate(self.pusch_su_index):  # Store the number of rbs for the same su index
                if su_index == value:
                    n_rb_per_su += self.n_rbs_per_pusch_su[index]
                else:
                    final_index = index
                    break
            if final_index == 0:
                final_index = len(self.pusch_su_index)

            for i in range(final_index):
                self.pusch_su_index.pop(0)
                self.n_rbs_per_pusch_su.pop(0)
                pusch.add_rb_indexes(rb_indexes=self.pusch_rb_index[0])
                self.pusch_rb_index.pop(0)
            pusch.set_occupied_os(n_os=self.n_os_pusch)
            pusch.set_occupied_resource_blocks(n_rb=n_rb_per_su)
            pusch.set_max_total_bytes(max_total_bytes=self.bytes_per_pusch * n_rb_per_su)
            if n_bytes_overhead_5g_nr is None:
                # FIXME: To be removed when we will add one header per packet when instantiating the UEs
                bytes_counter = 0  # Count the number of bytes that are mapped to the current PUSCH
            else:
                bytes_counter = n_bytes_overhead_5g_nr  # FIXME: Currently we add one header for all packets

            # Fill the PUSCH with all packets in the queue according to the right selection criteria
            packet_id_to_be_removed = list()
            for p in self.ul_buffer.get_packet_list():
                p.update_elapsed_time(current_time - p.get_generation_time())
                if p.get_elapsed_time() >= p.get_qos_latency():
                    print('WARNING: Packet {} discarded by UE {} before sending the PUSCH because '
                          'its deadline expires'.format(p.get_id(), self.get_ue_id()))
                    self.n_discarded_packets += 1
                    # TODO check other possible operations to be performed
                    # Save packet IDs to be removed
                    packet_id_to_be_removed.append(p.get_id())
                else:
                    mb_to_send = p.get_mb_to_sent()
                    bytes_counter += mb_to_send
                    pusch_max_total_bytes = pusch.get_max_total_bytes()
                    if bytes_counter > pusch_max_total_bytes:
                        bytes_counter -= mb_to_send  # Fill the PUCCH with part of the packet
                        n_bytes_remaining = pusch_max_total_bytes - bytes_counter
                        entry = pd.DataFrame([[p.get_ue_id(), p.get_id(), n_bytes_remaining, True,
                                               p.get_elapsed_time(), p.get_qos_latency()]],
                                             columns=["UE_ID", "Packet_ID", "Payload", "Partial",
                                                      "Elapsed_Time", "QoS_Latency"]
                                             )
                        pusch.add_queue_entry(entry)
                        break  # No more packets can be inserted in the PUSCH
                    else:
                        entry = pd.DataFrame([[p.get_ue_id(), p.get_id(), mb_to_send, False,
                                               p.get_elapsed_time(), p.get_qos_latency()]],
                                             columns=["UE_ID", "Packet_ID", "Payload", "Partial",
                                                      "Elapsed_Time", "QoS_Latency"]
                                             )

                        pusch.add_queue_entry(entry)
            # Remove packets that do not meet the qos_latency requirement
            for packet_id in packet_id_to_be_removed:
                self.ul_buffer.schedule_data(packet_id=packet_id)
                self.ul_buffer.remove_data(packet_id=packet_id)
            pusch_queue_request_df = pusch.get_queue_request_df()
            if not pusch_queue_request_df.empty:
                pusch.update_total_bytes()
                return pusch
            else:
                print('WARNING: UE {} cannot generate its PUSCH because either the packet queue is empty or '
                      'all packets do not meet their QOS latency requirement'.format(self.get_ue_id()))
                return None
        else:
            print('ERROR: UE {} cannot create its PUSCH because '
                  'it does not know the corresponding scheduling information'.format(self.get_ue_id()))
            return None

    def decode_harq(self, harq_list: List[HARQ]):
        """
           Find the HARQ intended for this UE and remove the (portion of) packets that have been correctly received

        Parameter
        --------
        harq_list : list
            List of HARQ classes

        Return
        ------
        None

        """

        for harq in harq_list:
            if harq.queue_packet_df.loc[0, "UE_ID"] == self.get_ue_id():
                for row, packet in harq.get_queue_request_df().iterrows():
                    # Remove (portion of) packets if they have been correctly received or if their deadline expires
                    if packet["Positive"] or packet["Expired"]:
                        self.schedule_packet(packet_id=packet["Packet_ID"])
                        # TODO: Francesco -> remove portion of packets by giving the amount of bytes to be removed
                        #  for each packet
                        self.remove_packet(packet_id=packet["Packet_ID"])
