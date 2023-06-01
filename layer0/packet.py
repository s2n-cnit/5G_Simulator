import pandas as pd

"""
    This class implements the packet data structure with
    associated properties.
"""


class Packet:

    def __init__(self):
        self.ue_id = 0
        self.packet_id = 0
        self.priority = 0
        self.size = 20  # Kb
        self.qos_latency = 0  # ticks
        self.qos_reliability = 0
        self.generation_time = 0  # tick of generation
        self.arrival_time = 0  # from generation time, in ticks
        self.n_transmissions = 1  # Number of times the packet has been transmitted
        self.mb_to_sent = 0  # remaining data to be sent
        self.min_mb_to_send = 0  # minimum number of bytes to be sent
        self.elapsed_time = 0  # Elapsed time since packet generation
        self.retx_attempt = 0

    def update_mb_to_sent(self, sent_data: float):
        """
            Update the Mb to sent to fully transmit this packet.
            Returns 1 if the packet has been fully transmitted, 0 otherwise.
        """
        self.mb_to_sent = max(0, int(self.mb_to_sent - sent_data))
        if self.mb_to_sent:
            return 0
        return 1

    def update_elapsed_time(self, time):
        self.elapsed_time = time - self.arrival_time

    def set_min_mb_to_send(self, bucket_size: int):
        self.min_mb_to_send = bucket_size

    def get_min_mb_to_send(self):
        return self.min_mb_to_send

    def get_elapsed_time(self):
        return self.elapsed_time

    def get_mb_to_sent(self):
        return self.mb_to_sent

    def set_mb_to_sent(self, mb_to_sent):
        self.mb_to_sent = mb_to_sent
    
    def get_transmission_counter(self):
        return self.n_transmissions
    
    def increment_transmission_counter(self):
        self.n_transmissions += 1

    def set_ue_id(self, input_ue_id: int):
        self.ue_id = input_ue_id

    def get_ue_id(self):
        return self.ue_id

    def set_id(self, input_packet_id: int):
        self.packet_id = input_packet_id

    def get_id(self):
        return self.packet_id

    def set_priority(self, input_priority: int):
        self.priority = input_priority

    def get_priority(self):
        return self.priority

    def set_qos_latency(self, input_qos_latency: float):
        self.qos_latency = input_qos_latency

    def get_qos_latency(self):
        return self.qos_latency

    def set_size(self, input_size: int):
        self.size = input_size

    def get_size(self):
        return self.size

    def set_qos_reliability(self, input_qos_reliability: float):
        self.qos_reliability = input_qos_reliability

    def get_qos_reliability(self):
        return self.qos_reliability

    def set_arrival_time(self, input_arrival_time: int):
        self.arrival_time = input_arrival_time

    def get_arrival_time(self):
        return self.arrival_time

    def set_generation_time(self, input_generation_time: int):
        self.generation_time = input_generation_time

    def get_generation_time(self):
        return self.generation_time

    def get_retx_attempt(self):
        return self.retx_attempt

    def increase_retx_attempt(self):
        self.retx_attempt += 1


class PUCCH(Packet):

    """
        PUCCH class that implements PUCCH features.
    """

    def __init__(self):
        super(PUCCH, self).__init__()
        self.queue_request_df = pd.DataFrame(columns=["UE_ID", "Packet_ID", "Priority", "Payload", "Bucket_Size",
                                                      "Retransmission", "Elapsed_Time", "QoS_Latency"])
        self.total_request_bytes = 0  # Total amount of bytes to be transmitted
        self.total_request_bucket_size = 0  # Total amount of bytes to be transmitted at minimum
        self.min_priority = 0  # Minimum packet priority in the queue, i.e. the most important level of request
        self.max_retransmission_number = 0  # Maximum number of times a single packet has been retransmitted
        self.max_deadline = 0  # Maximum deadline = elapsed_time/qos_latency, i.e. packet that should be transmitted
        # as soon as possible

    def add_queue_entry(self, df_entry):
        self.queue_request_df = self.queue_request_df.append(df_entry, ignore_index=True)

    def get_queue_request_df(self):
        return self.queue_request_df

    def update_request_bytes(self):
        self.total_request_bytes = self.queue_request_df['Payload'].sum()

    def get_total_request_bytes(self):
        self.update_request_bytes()
        return self.total_request_bytes

    def update_min_priority(self):
        self.min_priority = self.queue_request_df['Priority'].min()

    def get_queue_min_priority(self):
        self.update_min_priority()
        return self.min_priority

    def update_request_bucket_size(self):
        self.total_request_bucket_size = self.queue_request_df['Bucket_Size'].sum()

    def get_request_bucket_size(self):
        self.update_request_bucket_size()
        return self.total_request_bucket_size

    def update_max_retransmission_number(self):
        self.max_retransmission_number = self.queue_request_df['Retransmission'].max()

    def get_queue_max_retransmission_number(self):
        self.update_max_retransmission_number()
        return self.max_retransmission_number

    def update_max_deadline(self):
        self.max_deadline = (self.queue_request_df['Elapsed_Time']/self.queue_request_df['QoS_Latency']).max()

    def get_queue_max_deadline(self):
        self.update_max_deadline()
        return self.max_deadline

    def get_queue_ue_id(self):
        return self.queue_request_df.loc[0, "UE_ID"]  # It must be the same for all items


class PDCCH(Packet):

    """
        PDCCH class that implements PDCCH features.
    """

    def __init__(self):
        super(PDCCH, self).__init__()
        self.scheduling_info_dict = {
            'ue_id': 0,  # The ID of the recipient of this PDCCH
            'bytes_per_pusch': 0,  # Number of bytes that the recipient UE can map to each PUSCH
            'su_index': 0,  # The index of the scheduling unit in which the UE can transmit its PUSCH
            'n_rbs_per_su': 0,  # Number of resource blocks assigned for the transmission of the PUSCH
            'rb_index': 0  # Index of the resource blocks assigned for the transmission of the PUSCH
        }

    def set_scheduling_info(self, scheduling_info: dict):
        self.scheduling_info_dict.update(scheduling_info)

    def get_scheduling_info(self):
        return self.scheduling_info_dict

    def get_ue_id(self):
        return self.scheduling_info_dict.get('ue_id')


class PUSCH(Packet):

    """
        PUSCH class that implements PUSCH features.
    """

    def __init__(self):
        super(PUSCH, self).__init__()
        self.queue_packet_df = pd.DataFrame(columns=["UE_ID", "Packet_ID", "Payload", "Partial",
                                                     "Elapsed_Time", "QoS_Latency"])
        self.total_bytes = 0  # Total amount of bytes carried by the PUSCH
        self.max_total_bytes = 0  # Maximum amount of bytes that can be carried by the PUSCH
        self.n_rb = 0  # Number of resource blocks (i.e. 12 subcarriers) occupied by the PUSCH
        self.n_os = 0  # Number of OFDM symbols occupied by the PUSCH
        self.rb_index = list()  # List of resource block indexes which are occupied by the PUSCH

    def add_queue_entry(self, df_entry):
        self.update_total_bytes()
        actual_total_bytes = self.get_total_bytes()
        new_total_bytes = df_entry.loc[df_entry.first_valid_index(), 'Payload'] + actual_total_bytes
        if new_total_bytes > self.max_total_bytes:
            print('The PUSCH is full so the packet with ID {} cannot be inserted'.format(
                df_entry.loc[df_entry.first_valid_index(), 'Packet_ID']))
        else:
            self.queue_packet_df = self.queue_packet_df.append(df_entry, ignore_index=True)

    def get_queue_request_df(self):
        return self.queue_packet_df

    def update_total_bytes(self):
        self.total_bytes = self.queue_packet_df['Payload'].sum()

    def get_total_bytes(self):
        self.update_total_bytes()
        return self.total_bytes

    def set_max_total_bytes(self, max_total_bytes: int):
        self.max_total_bytes = max_total_bytes

    def get_max_total_bytes(self):
        return self.max_total_bytes

    def set_occupied_resource_blocks(self, n_rb: int):
        self.n_rb = n_rb

    def get_occupied_resource_blocks(self):
        return self.n_rb

    def set_occupied_os(self, n_os):
        self.n_os = n_os

    def get_occupied_os(self):
        return self.n_os

    def add_rb_indexes(self, rb_indexes: tuple):
        self.rb_index.append(rb_indexes)

    def get_rb_indexes(self):
        return self.rb_index


class HARQ(Packet):

    """
        HARQ class that implements HARQ features.
    """

    def __init__(self):
        super(HARQ, self).__init__()
        self.queue_packet_df = pd.DataFrame(columns=["UE_ID", "Packet_ID", "Payload", "Positive", "Expired"])

    def add_queue_entry(self, df_entry):
        self.queue_packet_df = self.queue_packet_df.append(df_entry, ignore_index=True)

    def get_queue_request_df(self):
        return self.queue_packet_df
