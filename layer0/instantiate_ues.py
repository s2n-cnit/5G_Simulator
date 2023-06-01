"""
    Utility scripts to create the UE list with the correct type of traffic

    @Note: simulator_tick_duration must be in seconds
"""

from ue import Ue
import sys
import math


def instantiate_ues(input_params_dict: dict, tot_number_of_ues: int, starting_state: str,
                    simulator_tick_duration: float):
    percentage_of_ue_counter = 0
    max_percentage_of_ue = 0
    ue_id = 0
    ue_list = []

    # Search all the types of input traffic and assign them to UEs 
    for key, values in input_params_dict.items():
        if key.startswith('traffic'):  # Pick-up input traffic parameters
            current_traffic_type = traffic_model[values["type"]]
            current_percentage_of_ue = values["percentage_of_ue"]
            qos_latency = values.get('qos_latency')
            qos_reliability = values.get('qos_reliability')
            priority = values.get('priority')
            payload = values.get('payload')
            bucket_size_perc = values.get('bucket_size_perc')
            current_number_of_nodes = math.ceil(current_percentage_of_ue/100 * tot_number_of_ues)
            percentage_of_ue_counter += current_percentage_of_ue  # Check that the percentage are correctly set in input
            
            # By using ceil we can have more UEs than the input number
            # so let us remove them from the traffic which is most diffused
            if max_percentage_of_ue <= current_percentage_of_ue: 
                max_percentage_of_ue = current_percentage_of_ue
                max_ue_list_index = len(ue_list)

            # Instantiate UEs that will generate the current traffic type
            for i in range(current_number_of_nodes):
                current_ue = Ue(input_params_dict, ue_id, current_traffic_type, starting_state)
                qos_latency_ticks = math.ceil(qos_latency*1e-3/simulator_tick_duration)
                current_ue.set_new_packet_qos_latency(qos_latency_ticks)
                current_ue.set_new_packet_qos_reliability(qos_reliability)
                current_ue.set_new_packet_priority(priority)
                current_ue.set_new_packet_size(payload)
                current_ue.set_mb_to_be_sent(payload)
                bucket_size = int(payload*bucket_size_perc/100)  # FIXME: Add the 5G protocol overhead
                current_ue.set_min_mb_to_be_send(bucket_size)

                if "period" in values.keys():
                    number_of_ticks = math.ceil(values["period"]/simulator_tick_duration)
                    current_ue.set_time_periodicity(number_of_ticks)
                    if "burst_size" in values.keys():
                        current_ue.set_burst_size(values.get("burst_size"))
                elif "random_model" in values.keys():
                    current_ue.set_random_model(values["random_model"])
                    if "burst_size" in values.keys():
                        current_ue.set_burst_size(values.get("burst_size"))
                    if "deterministic" in values.keys() and values.get('deterministic') is True:
                        new_max_generation_instant = \
                            round(current_ue.get_max_generation_instant()/values.get('deterministic_scale_factor'))
                        current_ue.set_max_generation_instant(new_max_generation_instant) 
                ue_list.append(current_ue)

    if percentage_of_ue_counter > 100 or percentage_of_ue_counter < 100:
        sys.exit('Check the percentage of UEs belonging to the different traffic types, their sum is not 100%!')
    else:
        if len(ue_list) > tot_number_of_ues:  # Remove excess UEs
            for i in range(len(ue_list) - tot_number_of_ues):                
                ue_list.pop(max_ue_list_index + i) 
        # Set UE ID now that the list is complete 
        for ue in range(len(ue_list)):
            ue_list[ue].set_ue_id(ue)
            ue_list[ue].set_ue_id_of_new_packet()
    return ue_list


# Dictionary to convert input numbers in string of traffic types
traffic_model = {
    1: "Periodic",
    2: "Aperiodic",
    3: "Burst Periodic",
    4: "Burst Aperiodic"
}
