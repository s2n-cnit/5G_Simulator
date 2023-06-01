import sys
import math
from typing import List

from g_node_b import GNodeB
from ue import Ue


class Geometry:
    """
        Geometry class that defines the factory geometrical specs, base on the use-case.
    """
    def __init__(self):
        self.factory_length = 0
        self.factory_width = 0
        self.factory_height = 0
        self.machine_size = 0
        self.inter_machine_distance = 0
        self.geometry_for_3gpp_channel_model = {
            'min_area_factory': 20,  # m^2
            'max_area_factory': 160000,  # m^2
            'min_factory_height': 5,  # m
            'max_factory_height': 25,  # m
            'max_UE_gNB_distance': 600,  # m
        }

    def set_use_case(self, use_case_input):
        if use_case_input == "Control-to-Control":  # 1
            self.factory_length = 100
            self.factory_width = 30
            self.factory_height = 10

        elif use_case_input == "Augmented Reality":  # 2
            self.factory_length = 20
            self.factory_width = 20
            self.factory_height = 4

        elif use_case_input == "Motion Control_Printing Machine":  # 3
            self.factory_length = 100
            self.factory_width = 100
            self.factory_height = 10 # was 30

        elif use_case_input == "Motion Control_Machine Tool":  # 4
            self.factory_length = 15
            self.factory_width = 15
            self.factory_height = 3

        elif use_case_input == "Motion Control_Packaging Machine":  # 5
            self.factory_length = 10
            self.factory_width = 5
            self.factory_height = 3

        elif use_case_input == "Remote Access and Maintenance":  # 6
            self.factory_length = 50
            self.factory_width = 10
            self.factory_height = 10

        elif use_case_input == "Mobile Control Panels_Assembly Robots":  # 7
            self.factory_length = 10
            self.factory_width = 10
            self.factory_height = 10

        elif use_case_input == "Mobile Control Panels_Mobile cranes":  # 8
            self.factory_length = 40
            self.factory_width = 60
            self.factory_height = 10

        elif use_case_input == "Mobile Robots":  # 9
            self.factory_length = 2000
            self.factory_width = 500
            self.factory_height = 10

        elif use_case_input == "Closed-Loop Process Control":  # 10
            self.factory_length = 100
            self.factory_width = 100
            self.factory_height = 50
            # self.machine_size = 10
            # self.inter_machine_distance = 40

        elif use_case_input == "Bi-rex":
            self.factory_length = 16
            self.factory_width = 33
            self.factory_height = 6

        # dding new use case>> factory size is like uc 3
        elif use_case_input == "fix-ue":  # 12
            self.factory_length = 100
            self.factory_width = 100
            self.factory_height = 10 # was 30
       
        else:
            sys.exit('Use case not recognized, check the spelling')

        # Scale the factory length, width and height to respect the 3GP channel model
        area_factory = self.factory_length * self.factory_width
        min_factory_area = self.geometry_for_3gpp_channel_model.get('min_area_factory')
        max_factory_area = self.geometry_for_3gpp_channel_model.get('max_area_factory')
        min_factory_height = self.geometry_for_3gpp_channel_model.get('min_factory_height')
        max_factory_height = self.geometry_for_3gpp_channel_model.get('max_factory_height')
        max_ue_g_node_b_distance = self.geometry_for_3gpp_channel_model.get('max_UE_gNB_distance')

        if area_factory < min_factory_area:
            self.factory_width = int(math.floor(min_factory_area / self.factory_length))

        if area_factory > max_factory_area:
            self.factory_width = int(math.floor(max_factory_area / self.factory_length))

        if self.factory_height < min_factory_height:
            self.factory_height = min_factory_height

        if self.factory_height > max_factory_height:
            self.factory_height = max_factory_height   

        # Scale the factory to host the maximum gNB-UE distance
        actual_max_ue_g_node_b_distance = math.sqrt(math.pow(self.factory_length/2, 2) +
                                                    math.pow(self.factory_width/2, 2) +
                                                    math.pow(self.factory_height, 2))
        # FIXME: When multiple gNB are deployed

        if actual_max_ue_g_node_b_distance > max_ue_g_node_b_distance:
            self.factory_length = int(math.floor(
                2 * math.sqrt(math.pow(max_ue_g_node_b_distance, 2) - math.pow(self.factory_width/2, 2) -
                              math.pow(self.factory_height, 2))))

    def get_factory_dimensions(self):
        return [self.factory_length, self.factory_width, self.factory_height]
    
    def set_machine_size(self, factory_length, factory_width, factory_height, machine_size, inter_machine_distance):
        # change min to 1 machine
        # min_number_of_machines = 10
        min_number_of_machines = 1

        m_distance = 1
        factory_list_tot = [factory_length, factory_width, factory_height]
        factory_min_tot = min(factory_list_tot)
        factory_list_length_width = [factory_length, factory_width]
        factory_min_length_width = min(factory_list_length_width)

        if machine_size >= factory_length or machine_size >= factory_width or machine_size >= factory_height:
            # check if the machine size is too big for the considered factory
            machine_size = factory_min_tot - m_distance
        
        if machine_size + inter_machine_distance > factory_length or machine_size + inter_machine_distance > \
                factory_width:
            inter_machine_distance = factory_min_length_width - machine_size

            if inter_machine_distance <= machine_size:
                inter_machine_distance = machine_size + m_distance

        area_factory = (self.factory_length-(machine_size/2))*(self.factory_width-(machine_size/2))
        area_machine = pow(machine_size, 2)
        area_machine_inter_machine = pow(inter_machine_distance, 2)
         
        if inter_machine_distance > machine_size:
            if area_factory/area_machine_inter_machine <= min_number_of_machines:
                inter_machine_distance = math.floor((pow(area_factory/min_number_of_machines, 1/2)))
                if machine_size >= inter_machine_distance:
                    machine_size = inter_machine_distance - m_distance
                    if machine_size <= 0:
                        machine_size = m_distance
                        if machine_size == inter_machine_distance:
                            inter_machine_distance = machine_size + m_distance
                    if area_factory/area_machine < min_number_of_machines:
                        machine_size = inter_machine_distance - m_distance

        else:
            if area_factory//area_machine < min_number_of_machines:
                machine_size = math.floor((pow(area_factory/min_number_of_machines, 1/2))) - 1
                inter_machine_distance = machine_size + m_distance

        if machine_size == inter_machine_distance:
            if machine_size != m_distance:
                machine_size = machine_size - m_distance
            else:
                inter_machine_distance = inter_machine_distance + m_distance
         
        self.machine_size = machine_size
        self.inter_machine_distance = inter_machine_distance

    def get_machine_size(self):
        return self.machine_size
        
    def get_inter_machine_distance(self):
        return self.inter_machine_distance       

    def set_ue_g_node_b_distances(self, ue_list: List[Ue], g_node_b: GNodeB):

        for index, ue in enumerate(ue_list):
            x = ue.get_coordinates()[0] - g_node_b.get_coordinates()[0] 
            y = ue.get_coordinates()[1] - g_node_b.get_coordinates()[1] 
            z = ue.get_coordinates()[2] - g_node_b.get_coordinates()[2]   

            ue_g_node_b_distance = math.sqrt(math.pow(x, 2) + math.pow(y, 2) + math.pow(z, 2))

            ue.set_distance_from_g_node_b(ue_g_node_b_distance)
