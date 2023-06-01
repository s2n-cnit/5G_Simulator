import pandas as pd
import copy as cp
import math
import operator

from typing import List

from ue import Ue
from packet import PUCCH, PDCCH, PUSCH, HARQ
from ue_buffer import UeBuffer
from get_bytes_per_pusch import get_bytes_per_pusch
from get_modulation_order import get_modulation_order


class CentralizedScheduler:

    def __init__(self, params, n_channels: int, ues_list: List[Ue]):
        self.frame_duration = params.get('radio').get('frame_duration')
        self.subframe_duration = params.get('radio').get('subframe_duration')
        self.carrier_frequency = params.get('radio').get('carrier_frequency')
        self.subcarrier_spacing = params.get('radio').get('subcarrier_spacing')
        self.n_os_su = params.get('radio').get('n_os_su')
        self.n_control_su = params.get('radio').get('n_control_su')
        self.n_processing_os_pucch_g_node_b = params.get('radio').get('n_processing_os_pucch_g_node_b')
        self.n_processing_os_pdcch_ue = params.get('radio').get('n_processing_os_pdcch_ue')
        self.n_os_pusch = params.get('radio').get('n_os_pusch')
        self.n_os_tx_rx_switch = params.get('radio').get('n_os_tx_rx_switch')
        self.n_subcarriers_per_pusch = params.get('radio').get('n_subcarriers_per_pusch')
        self.n_bytes_overhead_5g_nr = params.get('radio').get('n_bytes_overhead_5g_nr')
        self.scheduler_type = params.get('simulation').get('scheduling')
        self.n_channels = n_channels
        self.n_su_per_subframe = int(2 * self.subcarrier_spacing/15)  # Number of scheduling unit per subframe
        self.n_processing_su = math.ceil((self.n_processing_os_pucch_g_node_b + self.n_processing_os_pdcch_ue) /
                                         self.n_os_su)
        self.n_data_su = self.n_su_per_subframe - self.n_control_su - self.n_processing_su  # Number of scheduling unit
        # per subframe used for data
        self.n_pusch_rb = \
            self.n_subcarriers_per_pusch * self.n_channels * self.n_data_su  # Overall number of available resource
        # blocks dedicated to PUSCH within a group of 56 os
        if self.n_data_su <= 0:
            self.data_su_counter = self.n_su_per_subframe  # PUCCH periodicity is enlarged by one subframe
            # due to additional control and processing latencies
            self.n_data_su = self.data_su_counter
        else:
            self.data_su_counter = self.n_data_su
        self.ues_list = ues_list
        self.n_ues = len(ues_list)
        # We can simulate one or both types of traffic
        self.ues_dl_buffer = self.__initialize_dl_buffer()
        self.ues_ul_buffer = []
        self.received_pucch_df = pd.DataFrame(columns=["UE_ID", "Priority", "Payload", "Bucket_Size", "Bytes_per_PUSCH",
                                                       "Retransmission", "Deadline", "Network_Enjoyment_Level"])
        self.network_enjoyment_level_df = pd.DataFrame(columns=["UE_ID", "Network_Enjoyment_Level"])

    def __initialize_dl_buffer(self):
        # Reference to Ues' buffers to keep track of users' requests
        return [UeBuffer() for ue in self.ues_list]

    def get_ues_ul_buffer(self, ues_set: List[int] = None):
        """
            The scheduler does not have access to uplink buffers unless it asks for
            them to the users.
        """
        ues_ul_buffers = dict()
        if ues_set is None:
            ues_set = pd.arange(self.n_ues)
        for ue_id in ues_set:
            ues_ul_buffers[ue_id] = self.ues_list[ue_id].get_ul_buffer()
        """
            Schedule uplink traffic
        """
        return 

    def assign_pucch_to_ues(self, simulator_tick_duration: float): 
        """
            The scheduler assigns at each UE the resource to be used for scheduling requests (via PUCCH)
        """
        # Compute the PUCCH periodicity for the first group of n_channels UEs 
        # NOTE: The last group may be incomplete depending on the number of UEs
        # NOTE: We are assuming the the PUCCH is one scheduling unit (7 os) long and one PUCCH per subframe 
        n_pucch_to_assign = math.ceil(self.n_ues / self.n_channels)
        n_added_subframe = int(self.n_data_su / self.n_su_per_subframe)  # If there is no room for data su in a
        # subframe, enlarge the pucch periodicity by another one
        pucch_periodicity = (n_pucch_to_assign + n_pucch_to_assign * n_added_subframe) * self.subframe_duration * 1e-3
        pucch_periodicity_g_node_b = (1 + n_added_subframe) * self.subframe_duration * 1e-3

        # Order UEs according to their priority and qos requirement
        self.ues_list = sorted(self.ues_list, reverse=False, key=operator.attrgetter('packet.priority',
                                                                                     'packet.qos_latency'))

        ue = 0
        start_of_band = self.carrier_frequency - math.ceil(self.n_channels / 2) * 12 * self.subcarrier_spacing * 1e-6
        # GHz
        channel_bandwidth = 12 * self.subcarrier_spacing * 1e-6  # GHz
        for pucch_index in range(n_pucch_to_assign): 
            for channel in range(self.n_channels):
                # ***30 kHz ***
                # t_generation tra 0 e 28
                initial_offset_pucch_transmission = (self.subframe_duration * (pucch_index + 1) + pucch_index *
                                                     self.subframe_duration) * 1e-3  # s #NOTE: First subframe is
                
                # *** 60 kHz ***
                # initial_offset_pucch_transmission = ((pucch_index+1) * (self.subframe_duration)) * 1e-3 # s
                self.ues_list[ue].initial_offset_pucch_transmission_ticks = math.ceil(
                    int(initial_offset_pucch_transmission / simulator_tick_duration))  # Ticks
                self.ues_list[ue].update_state_duration(self.ues_list[ue].initial_offset_pucch_transmission_ticks)
                # First tick for PUCCH generation (if queue is not empty)
                scheduling_request_periodicity = int(pucch_periodicity / simulator_tick_duration)  # Ticks
                self.ues_list[ue].set_scheduling_request_periodicity(scheduling_request_periodicity)
                self.ues_list[ue].pucch = n_pucch_to_assign 
                self.ues_list[ue].scheduling_request_carrier_frequency = \
                    start_of_band + channel * channel_bandwidth + channel_bandwidth/2
                self.ues_list[ue].set_carrier_frequency(self.ues_list[ue].scheduling_request_carrier_frequency)
                self.ues_list[ue].scheduling_request_channel = channel
                g_node_b_scheduling_request_periodicity = int(pucch_periodicity_g_node_b / simulator_tick_duration)
                # Ticks
                self.ues_list[ue].set_scheduling_request_periodicity_g_node_b(g_node_b_scheduling_request_periodicity)
                self.ues_list[ue].set_channel(channel)

                if ue + 1 < self.n_ues:
                    ue += 1
                else:                                           
                    break

        return self.ues_list

    def assign_pdcch_to_g_node_b(self, simulator_tick_duration: float):
        """
            The scheduler assigns at gNB the resource to be used for scheduling response (via PDCCH) to be sent to
            different UEs
        """
        # Compute the PDCCH periodicity for the first group of n_channels UEs 
        # NOTE: The last group may be incomplete depending on the number of UEs
        # NOTE: We are assuming the the PDCCH is one scheduling unit (7 os) long and one PDCCH per subframe,
        # scheduled in the second slot available after PUCCH
        
        n_pdcch_to_assign = math.ceil(self.n_ues / self.n_channels)
        n_added_subframe = int(self.n_data_su / self.n_su_per_subframe)  # If there is no room for data su
        # in a subframe, enlarge the pucch periodicity by another one
        pdcch_periodicity = (n_pdcch_to_assign + n_pdcch_to_assign * n_added_subframe) * self.subframe_duration * 1e-3

        ue = 0
        start_of_band = self.carrier_frequency - math.ceil(self.n_channels / 2) * 12 * self.subcarrier_spacing * 1e-6
        # GHz
        channel_bandwidth = 12 * self.subcarrier_spacing * 1e-6  # GHz
        for pdcch_index in range(n_pdcch_to_assign): 
            for channel in range(self.n_channels):
                self.ues_list[ue].initial_offset_pdcch_transmission_ticks = \
                    self.ues_list[ue].initial_offset_pucch_transmission_ticks + self.subframe_duration/2
                self.ues_list[ue].scheduling_response_periodicity = int(pdcch_periodicity /
                                                                        simulator_tick_duration)  # Ticks
                self.ues_list[ue].scheduling_response_carrier_frequency = \
                    start_of_band + channel * channel_bandwidth + channel_bandwidth/2
                self.ues_list[ue].scheduling_response_channel = channel
                self.ues_list[ue].set_channel(channel)
                if ue + 1 < self.n_ues:
                    ue += 1
                else:                                           
                    break

    def set_n_pusch_rb(self, n_pusch_rb: int):
        self.n_pusch_rb = n_pusch_rb

    def get_n_pusch_rb(self):
        return self.n_pusch_rb

    def decode_received_pucchs(self, pucch_list: List[PUCCH], snr_list_db: List[float]):
        """
            From the list of received PUCCHs and the corresponding SNR fill a dataframe containing all the proper info
            for performing the scheduling
        """

        # Clear the dataframe containing previous received PUCCHs, if any
        if not self.received_pucch_df.empty:
            self.received_pucch_df = self.received_pucch_df.drop(labels=range(len(self.received_pucch_df)))

        for row, pucch in enumerate(pucch_list):
            self.received_pucch_df.loc[row, "UE_ID"] = pucch.get_queue_ue_id()
            self.received_pucch_df.loc[row, "Retransmission"] = pucch.get_queue_max_retransmission_number()
            self.received_pucch_df.loc[row, "Priority"] = pucch.get_queue_min_priority()
            self.received_pucch_df.loc[row, "Payload"] = pucch.get_total_request_bytes()
            self.received_pucch_df.loc[row, "Bucket_Size"] = pucch.get_request_bucket_size()
            self.received_pucch_df.loc[row, "Deadline"] = pucch.get_queue_max_deadline()

            net_enj_lev = 0  # If the UE has not yet asked any resource, the network enjoyment level is 0
            for index, row_value in self.network_enjoyment_level_df.iterrows():
                if row_value["UE_ID"] == pucch.get_queue_ue_id():
                    net_enj_lev = row_value["Network_Enjoyment_Level"]

            self.received_pucch_df.loc[row, "Network_Enjoyment_Level"] = net_enj_lev
            # Set bytes that each PUSCH will carry according to the SNR characterizing each received PUCCH
            modulation_order = get_modulation_order(self.scheduler_type, snr_list_db[row])
            n_bytes_per_pusch = get_bytes_per_pusch(self.n_subcarriers_per_pusch, self.n_os_pusch, modulation_order)
            self.received_pucch_df.loc[row, "Bytes_per_PUSCH"] = n_bytes_per_pusch

    def get_received_pucchs(self):
        return self.received_pucch_df

    def generate_pdcch_list(self):
        """
            The scheduler generates a list of PDCCH, one for each UE which has successfully sent its PUCCH
        """

        n_requesting_ues = len(self.received_pucch_df.index)

        if n_requesting_ues > 0:

            # Order pucchs
            ordered_pucch_df = self.received_pucch_df.sort_values(
                ["Priority", "Deadline", "Retransmission", "Network_Enjoyment_Level"],
                ascending=(True, True, False, True))

            # Assign scheduling unit (su) and channel indexes per each request
            su_list = list()
            n_rbs_per_su_list = list()
            rb_index_list = list()
            pdcch_list = list()
            su_counter = 0
            rb_index_counter = 0

            for iteration in range(2):  # Assign the bucket size first and then the remaining payload, if any
                for row, pucch in ordered_pucch_df.iterrows():
                    if iteration == 0:
                        # We are scanning the PUCCH dataframe for the bucket size
                        # FIXME: Assign resources so that we have one 5G protocol header per packet,
                        #  i.e remove the term self.n_bytes_overhead_5g_nr if it has been counted when the packet
                        #  structure field of the UE is instantiated
                        data_to_transmit_bytes = pucch["Bucket_Size"] + self.n_bytes_overhead_5g_nr
                    else:
                        # We are scanning the PUCCH dataframe for the remaining part of the bytes
                        data_to_transmit_bytes = pucch["Payload"] - pucch["Bucket_Size"]

                    n_pusch_needed = math.ceil(data_to_transmit_bytes/pucch["Bytes_per_PUSCH"])  # NOTE:
                    # This approximation means that the last resource block is not fully utilized

                    su_list.append(su_counter)
                    rb_index_start = rb_index_counter  # To understand the channel indexes associated to each SU
                    for pusch in range(n_pusch_needed):
                        rb_index_counter += 1
                        if rb_index_counter > self.n_channels - 1:
                            rb_index_stop = rb_index_counter
                            rb_index_list.append((rb_index_start, rb_index_stop - 1))
                            n_rbs_per_su_list.append(rb_index_stop - rb_index_start)
                            rb_index_counter = 0
                            rb_index_start = 0
                            su_counter += 1
                            if su_counter >= self.n_data_su:
                                print("The number of resources is not sufficient to host all UEs!!")
                                break
                            else:
                                su_list.append(su_counter)

                    rb_index_stop = rb_index_counter
                    if rb_index_start != 0 or rb_index_stop != 0:  # If there are no free resources left these
                        # two counters are 0
                        rb_index_list.append((rb_index_start, rb_index_stop - 1))
                        n_rbs_per_su_list.append(rb_index_stop - rb_index_start)

                    if iteration == 0:
                        # Create the PDCCH for this UE and append it to the list of PDCCH
                        scheduling_info_dict = {
                            'ue_id': cp.copy(pucch["UE_ID"]),
                            'bytes_per_pusch': cp.copy(pucch["Bytes_per_PUSCH"]),
                            'su_index': cp.copy(su_list),
                            'n_rbs_per_su': cp.copy(n_rbs_per_su_list),
                            'rb_index': cp.copy(rb_index_list)
                        }
                        pdcch = PDCCH()
                        pdcch.set_scheduling_info(scheduling_info=scheduling_info_dict)
                        pdcch_list.append(cp.copy(pdcch))
                    else:
                        # Update the PDCCH of the current UE if there were resources to be assigned
                        if n_pusch_needed > 0:
                            for index, pdcch in enumerate(pdcch_list):
                                if pdcch.get_ue_id() == pucch["UE_ID"]:
                                    # Concatenate old and new lists
                                    pdcch.scheduling_info_dict["su_index"] = \
                                        pdcch.scheduling_info_dict["su_index"] + su_list
                                    pdcch.scheduling_info_dict["n_rbs_per_su"] = \
                                        pdcch.scheduling_info_dict["n_rbs_per_su"] + n_rbs_per_su_list
                                    pdcch.scheduling_info_dict["rb_index"] = \
                                        pdcch.scheduling_info_dict["rb_index"] + rb_index_list

                    # Clear lists for the new request
                    su_list.clear()
                    n_rbs_per_su_list.clear()
                    rb_index_list.clear()

                    if su_counter >= self.n_data_su:
                        break  # Exit for loop because there are no more free resources

                if su_counter >= self.n_data_su:
                    break  # Exit for loop because there are no more free resources

            # Compute the network enjoyment level for each UE and store it
            for row, pucch in ordered_pucch_df.iterrows():
                for index, pdcch in enumerate(pdcch_list):
                    if pdcch.get_ue_id() == pucch["UE_ID"]:
                        n_pusch_assigned = sum(pdcch.scheduling_info_dict.get('n_rbs_per_su'))
                        n_pusch_needed = math.ceil((pucch["Bucket_Size"] +
                                                    self.n_bytes_overhead_5g_nr)/pucch["Bytes_per_PUSCH"])
                        n_pusch_needed += math.ceil((pucch["Payload"] - pucch["Bucket_Size"])/pucch["Bytes_per_PUSCH"])
                        network_enjoyment_level = n_pusch_assigned / n_pusch_needed
                        ue_df = self.network_enjoyment_level_df.loc[self.network_enjoyment_level_df["UE_ID"] ==
                                                                    pucch["UE_ID"]]
                        if not ue_df.empty:
                            self.network_enjoyment_level_df.loc[ue_df.index, "Network_Enjoyment_Level"] += \
                                network_enjoyment_level
                        else:
                            n_rows = len(self.network_enjoyment_level_df.index)
                            self.network_enjoyment_level_df.loc[n_rows + 1, "UE_ID"] = pucch["UE_ID"]
                            self.network_enjoyment_level_df.loc[n_rows + 1, "Network_Enjoyment_Level"] = \
                                0  # Initialization
                            self.network_enjoyment_level_df.loc[n_rows + 1, "Network_Enjoyment_Level"] += \
                                network_enjoyment_level

            # Return the PDCCH list
            return pdcch_list

        else:
            print('WARNING: The scheduler cannot produce a PDCCH because it has not received any PUCCH')
            return None

    def decode_received_puschs(self, core_network_delay: int, simulator_tick_duration: float, pusch_list: List[PUSCH],
                               is_received: List[bool]):
        """
            From list of received PUSCHs to list of HARQs to be transmitted

            Parameter
            --------
            core_network_delay : int
                Core network delay in ms

            simulator_tick_duration: float
                Tick duration in s

            pusch_list : List
                List of PUSCH elements

            is_received : List
                List of booleans, true if the corresponding PUSCH has been correctly received, false otherwise

            Return
            ------
            harq_list : List
                List of HARQ elements

            e2e_latency : Dataframe
                Dataframe of E2E latencies for each UE and each packet
        """

        harq_list = list()
        harq_entry = pd.DataFrame(columns=["UE_ID", "Packet_ID", "Payload", "Positive", "Expired"])
        e2e_latency = pd.DataFrame(columns=["UE_ID", "Packet_ID", "E2E_Latency"])

        # Loop over the list of PUSCHs
        for pusch_index, pusch in enumerate(pusch_list):
            harq = HARQ()
            pusch_packet_queue = pusch.get_queue_request_df()
            harq_entry.loc[0, "UE_ID"] = pusch_packet_queue.loc[0, "UE_ID"]
            if not is_received[pusch_index]:
                harq_entry.loc[0, "Positive"] = False  # PUSCH not correctly received
            else:
                harq_entry.loc[0, "Positive"] = True  # PUSCH correctly received

            # Loop over the list of packets contained in the current PUSCH
            for row, packet in pusch_packet_queue.iterrows():
                harq_entry.loc[0, "Packet_ID"] = packet["Packet_ID"]
                harq_entry.loc[0, "Payload"] = packet["Payload"]

                # Check that the packet deadline has not expired
                packet["Elapsed_Time"] += self.n_os_pusch + self.n_os_tx_rx_switch  # HARQ generated after 5 os from
                # PUSCH transmission
                if packet["Elapsed_Time"] >= packet["QoS_Latency"]:
                    harq_entry.loc[0, "Expired"] = True  # The packet deadline has expired
                else:
                    harq_entry.loc[0, "Expired"] = False  # The packet deadline has not expired

                    if not packet["Partial"]:
                        e2e_latency = e2e_latency.append(
                            pd.DataFrame(
                                [[packet["UE_ID"], packet["Packet_ID"],
                                  packet["Elapsed_Time"] * simulator_tick_duration * 1e3 + core_network_delay]],
                                columns=["UE_ID", "Packet_ID", "E2E_Latency"]), ignore_index=True)

                harq.add_queue_entry(harq_entry)

            harq_list.append(harq)

        return harq_list, e2e_latency
