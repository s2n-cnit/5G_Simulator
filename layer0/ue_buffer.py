import operator

from packet import Packet


class UeBuffer:
    """
        This class implements a user buffer, i.e., a collection of packets.
    """

    def __init__(self):
        self.packet_list = []  # Contains all generated and not yet sent packets
        self.pending_packet_id = None  # Contains the scheduled packet (one tx at a time ! )
        self.packet_id_set = set()  # Contains the ids of the packets in 'packet_list'
        self.buffer_size = 0  # Number of bits in the buffer
        self.n_packets = 0  # Number of packets in the buffer
        self.pending = False
        self.max_buffer_size = 100000  # bytes

    def add_packet(self, packet: Packet):
        """
            Add a new packet to the buffer, updating the buffer size, if the buffer is not full
        """
        if self.buffer_size + packet.size < self.max_buffer_size:
            self.packet_list.append(packet)
            self.packet_id_set.add(packet.get_id())
            self.buffer_size += packet.size
            self.n_packets += 1
            return True
        else:
            return False

    def schedule_data(self, priority_metric: str = None, packet_id: int = None, tx_size: float = None):
        """
            Schedule tx_size Mb or specific packet_id packet from this buffer. Return 0 if not empty, 1 otherwise.
        """

        if self.buffer_size == 0:
            return 1
        if priority_metric is not None:
            self.order_buffer(priority_metric)

        # For now transmit packets
        if packet_id is not None:
            # Add packet to the pending ones
            if packet_id in self.packet_id_set:
                self.pending_packet_id = packet_id
                self.pending = True
            else:
                print(
                    "Attention ! The packet with id {} "
                    "is not in the buffer and it cannot be scheduled for transmission".format(packet_id))
        else:
            # TODO partial packet transmission
            return

        if self.buffer_size:
            return 0
        return 1

    def order_buffer(self, priority_metric):
        # Order packets by priority and qos_latency requirement to choose the one that needs resources
        self.packet_list = sorted(self.packet_list, reverse=False,
                                  key=operator.attrgetter(priority_metric))

    def find_packet_by_id(self, packet_id: int):
        """
            Return the list index of the packet with id == 'packet_id'.
        """
        for idx in range(self.n_packets):
            if self.packet_list[idx].get_id() == packet_id:
                return idx

    def get_packet_by_id(self, packet_id: int):
        return self.packet_list[self.find_packet_by_id(packet_id)]

    def remove_data(self, packet_id: int):
        """
            Remove data (now packets) from the buffer once the ack has been received.
        """
        if packet_id != self.pending_packet_id:
            print("The packet {} was not scheduled and cannot be removed".format(packet_id))
        elif packet_id not in self.packet_id_set:
            print("Attention ! The packet with id {} is not in the buffer and it cannot be removed".format(packet_id))
        else:
            self.pending_packet_id = None
            self.pending = False
            idx_packet = self.find_packet_by_id(packet_id)
            # Update buffer size and number of total packets
            self.buffer_size -= self.packet_list[idx_packet].get_size()
            self.n_packets -= 1
            self.packet_id_set.remove(packet_id)
            del self.packet_list[idx_packet]

    def get_first_packet(self):
        return self.packet_list[0]

    def get_buffer_size(self):
        return self.buffer_size

    def get_n_packets(self):
        return self.n_packets

    def get_packet_list(self):
        return self.packet_list

    # TODO : TO BE REMOVED AFTER DEBUGGING !!!
    def set_packet_list(self, packet_list):
        self.packet_list = packet_list

    def get_pending_packet_id(self):
        return self.pending_packet_id

    def is_pending(self):
        return self.pending

    def get_first_packet_id(self):
        return self.packet_list[0].get_id()
