import sys
import math
import random
from pandas.core.frame import DataFrame

from ue import Ue
from g_node_b import GNodeB
from machine import Machine
from typing import List


class Distribution:
    """
        Distribute devices on the environment and compute LoS condition.
    """
    def __init__(self, use_case: str, factory_length: int, factory_width: int, ue_distribution: str,
                 machine_size: int = None, inter_machine_distance: int = None,
                 birex_df: DataFrame = None, tot_number_of_ues: int = None, machine_list_len= 1, machine_height: int = 3):
        self.type = ue_distribution
        if machine_size is not None and inter_machine_distance is not None:
            self.machine_size = machine_size
            self.machine_height = machine_height
            self.inter_machine_distance = inter_machine_distance
            # change the number of machines into 1 for x and y
            # why define machine position for x and y !!
            # I put another if to set for our use-case
            # self.number_of_machines_on_x = 1
            self.number_of_machines_on_x = \
                        1 + math.floor((factory_length-self.machine_size)/self.inter_machine_distance)
            self.number_of_machines_on_y = \
                        1 + math.floor((factory_width-self.machine_size)/self.inter_machine_distance)
        elif use_case != "Bi-rex":
            sys.exit('Provide the machine size and inter machine distance to Distribution class!')

        if use_case == "Control-to-Control":  # 1
            self.ue_density = 0.003
            
        elif use_case == "Augmented Reality":  # 2
            self.ue_density = 0.08

        elif use_case == "Motion Control_Printing Machine":  # 3
            self.ue_density = 0.1
           
        elif use_case == "Motion Control_Machine Tool":  # 4
            self.ue_density = 0.1
              
        elif use_case == "Motion Control_Packaging Machine":  # 5
            self.ue_density = 0.1

        elif use_case == "Remote Access and Maintenance":  # 6
            self.ue_density = 0.5

        elif use_case == "Mobile Control Panels_Assembly Robots":  # 7
            self.ue_density = 0.04

        elif use_case == "Mobile Control Panels_Mobile cranes":  # 8
            self.ue_density = 0.04

        elif use_case == "Mobile Robots":  # 9
            self.ue_density = 0.1

        elif use_case == "Closed-Loop Process Control":  # 10
            self.ue_density = 0.002

        elif use_case == "Bi-rex":  # 11
            self.ue_density = 0  # Not used for this use-case

        # added new if >> zero ue attached to device
        elif use_case == "fix-ue": # 12

            self.ue_density = 0
            # self.tot_number_of_machines = self.number_of_machines_on_x * self.number_of_machines_on_y
            # self.tot_number_of_ues = math.ceil(self.ue_density * pow(machine_size, 3)) * self.tot_number_of_machines
            # print(f">>>Distribution>>>fix-ue is seclected and tot_number_of_ues is {self.tot_number_of_ues}")
            # tot_number_of_ues = 0
        else:
            sys.exit('Use case not recognized, check the spelling') 

        if use_case == "Bi-rex":
            self.tot_number_of_machines = len(birex_df.index) - 2  # First row for bi.rex layout,
            # second row for gNB coordinates
            self.tot_number_of_ues = tot_number_of_ues

        # Add new number of machines based on input
        elif use_case == "fix-ue": # 12:
            self.tot_number_of_machines = machine_list_len
            self.tot_number_of_ues = math.ceil(self.ue_density * pow(machine_size, 3)) * self.tot_number_of_machines
            # tot_number_of_ues = 0
        else:
            self.tot_number_of_machines = self.number_of_machines_on_x * self.number_of_machines_on_y
            # is this the number of ues can be attached to each machine ?
            self.tot_number_of_ues = math.ceil(self.ue_density*pow(machine_size, 3)) * self.tot_number_of_machines

    def distribute_machines(self, machines: List[Machine], birex_df: DataFrame = None):
        if birex_df is not None:
            for birex_df_row, machine in enumerate(machines):  # Machines in df starts from row 2
                x = birex_df.loc[birex_df_row + 2, 'X-center']
                y = birex_df.loc[birex_df_row + 2, "Y-center"]
                z = birex_df.loc[birex_df_row + 2, "Height"]
                machine.set_machine_size(z)
                machine.set_coordinates(x, y, z/2)
                machine.set_max_number_of_ues(self.tot_number_of_ues)  # UEs may, in principle, be located just
                # in a single machine
        else:
            machine = 0
            for x in range(self.number_of_machines_on_x):
                for y in range(self.number_of_machines_on_y):
                    machines[machine].set_coordinates(self.machine_size/2 + self.inter_machine_distance * x,
                                                      self.machine_size/2 + self.inter_machine_distance * y,
                                                      self.machine_size/2
                                                      )
                    machines[machine].x_min = self.inter_machine_distance * x
                    machines[machine].x_max = self.machine_size + self.inter_machine_distance * x
                    machines[machine].y_min = self.inter_machine_distance * y
                    machines[machine].y_max = self.machine_size + self.inter_machine_distance * y
                    machine += 1

    def distribute_selective_machines(self, machines: List[Machine], machine_tile_x_ls, machine_tile_y_ls):
        for machine in range(len(machine_tile_x_ls)):
            machines[machine].set_coordinates(machine_tile_x_ls[machine],machine_tile_y_ls[machine],self.machine_size/2)
            machines[machine].x_min = machine_tile_x_ls[machine] - self.machine_size/2
            machines[machine].x_max = machine_tile_x_ls[machine] + self.machine_size/2
            machines[machine].y_min = machine_tile_y_ls[machine] - self.machine_size/2
            machines[machine].y_max = machine_tile_y_ls[machine] + self.machine_size/2
            print(f"Distribution.py>>>>distribute_selective_machines>>>>> "
                  f"Machine location is x= {machines[machine].x} and y={machines[machine].y} ")
    def set_distribution_type(self, d_type):
        self.type = d_type

    def get_distribution_type(self):
        return self.type

    def set_inter_machine_distance(self, inter_machine_distance: float):
        self.inter_machine_distance = inter_machine_distance

    def get_inter_machine_distance(self):
        return self.inter_machine_distance

    def get_number_of_machines(self):
        return self.tot_number_of_machines

    def set_machine_size(self, machine_size: float):
        self.machine_size = machine_size

    # Add machine height function (I  add machine height to machine class)
    def get_machine_height(self):
        return  self.machine_height

    def get_machine_size(self):
        return self.machine_size

    def distribute_ues(self, ues, machines, factory_length: int = None, factory_width: int = None):
        ue = 0
        ue_counter = 0
        max_machine_size = machines[0].get_machine_size()  # Bi-rex scenario can have machines of different size

        # Check that the number of machine is sufficient to host the current number of UEs
        for index, machine in enumerate(machines):
            ue_counter += machine.get_max_number_of_ues()
            new_machine_size = machine.get_machine_size()
            if new_machine_size > max_machine_size:
                max_machine_size = new_machine_size
        if len(ues) > ue_counter:
            sys.exit('The current number of machines cannot host such an amount of ues')

        while ue < len(ues):
            # Distribute UEs within the factory and check that the maximum number of UEs per machine is respected
            if self.type == 'Uniform':
                ues[ue].set_coordinates(random.uniform(0, factory_length),
                                        random.uniform(0, factory_width),
                                        random.uniform(0, max_machine_size)
                                        )
                x = ues[ue].get_coordinates()[0]
                y = ues[ue].get_coordinates()[1]
                z = ues[ue].get_coordinates()[2]
                ue += 1
                for index, machine in enumerate(machines):
                    if machine.x_min <= x <= machine.x_max and machine.y_min <= y <= machine.y_max and \
                            z <= machine.get_machine_size():
                        if machine.get_number_of_ues() + 1 <= machine.get_max_number_of_ues():
                            machine.add_new_ue()  # The machine where the UEs is located con host this new UE
            else:
                sys.exit('The ue distribution statistics is not recognized')

    def distribute_g_node_b(self, g_node_bs, x, y, z):  # FIXME: When the number of gNBs increases
        if isinstance(g_node_bs, list): 
            for g_node_b in range(len(g_node_bs)):
                g_node_bs[g_node_b].set_coordinates(x, y, z)   
        else:
            g_node_bs.set_coordinates(x, y, z)   

    def set_tot_number_of_ues(self, number_ue_input: int):
        if number_ue_input <= self.tot_number_of_ues:
            self.tot_number_of_ues = number_ue_input
        else:
            warning_string = 'WARNING: The number of UEs in input is too large, it has been truncated to ' \
                             'the maximum of ' + str(self.tot_number_of_ues) + ' UEs'
            print(warning_string)
    
    def get_tot_number_of_ues(self):
        return self.tot_number_of_ues

    def get_ue_density(self):
        return self.ue_density

    def are_ues_in_los(self, ue_list: List[Ue], g_node_b: GNodeB, machines: List[Machine]):
        # Pick-up gNB coordinates
        g_node_b_coordinates = g_node_b.get_coordinates()
        x_g_node_b = g_node_b_coordinates[0]
        y_g_node_b = g_node_b_coordinates[1]
        z_g_node_b = g_node_b_coordinates[2]

        for i, ue in enumerate(ue_list):
            is_in_los = True
            # Pick-up UE coordinates
            ue_coordinates = ue.get_coordinates()
            x_ue = ue_coordinates[0]
            y_ue = ue_coordinates[1]
            z_ue = ue_coordinates[2]
            x_diff = abs(x_g_node_b - x_ue)
            y_diff = abs(y_g_node_b - y_ue)

            # Check if the line linking UE and gNB intercepts a machine by sweeping it
            # with "step" discretization interval
            step = 0.1  # machines[0].get_machine_size() / 2
            #  FIXME: If the gNB can be at the same height of UEs other cases should be inserted
            if x_diff == 0 and y_diff != 0:
                # UE and gNB have the same abscissa, move on y-axis only
                x = x_ue
                y = min(y_ue, y_g_node_b)
                y_target = max(y_ue, y_g_node_b)
                while y <= y_target:
                    for index, machine in enumerate(machines):
                        if machine.x_min <= x <= machine.x_max and machine.y_min <= y <= machine.y_max:
                            z = (y - y_ue) / (y_g_node_b - y_ue) * (z_g_node_b - z_ue) + z_ue

                            # Add another parameter for height of machine (Add for all loops)
                            # if z <= machine.get_machine_size():
                            #     is_in_los = False  # Intersection, i.e NLOS
                            if z <= machine.get_machine_height():
                                is_in_los = False  # Intersection, i.e NLOS
                    # Search for the next point 
                    y += step  
            elif x_diff != 0 and y_diff == 0:
                # UE and gNB have the same ordinate, move on x-axis only
                y = y_ue
                x = min(x_ue, x_g_node_b)
                x_target = max(x_ue, x_g_node_b)
                while x <= x_target:
                    for index, machine in enumerate(machines):
                        if machine.x_min <= x <= machine.x_max and machine.y_min <= y <= machine.y_max:
                            z = (x - x_ue) / (x_g_node_b - x_ue) * (z_g_node_b - z_ue) + z_ue
                            # add height
                            if z <= machine.get_machine_height():
                                is_in_los = False  # Intersection, i.e NLOS
                            # if z <= machine.get_machine_size():
                            #     is_in_los = False  # Intersection, i.e NLOS
                    # Search for the next point 
                    x += step   
            elif x_diff == 0 and y_diff == 0:
                # UE and gNB have the same abscissa and ordinate:
                # just check if the UE is inside a machine, i.e move on z-axis only
                x = x_ue
                y = y_ue
                z = z_ue
                for index, machine in enumerate(machines): 
                    if machine.x_min <= x <= machine.x_max and machine.y_min <= y <= machine.y_max:
                        #  Add height
                        if z <= machine.get_machine_height():
                            is_in_los = False  # Intersection, i.e NLOS
                        # if z <= machine.get_machine_size():
                        #     is_in_los = False  # Intersection, i.e NLOS
            else:
                # UE and gNB have all different coordinates
                x = min(x_ue, x_g_node_b)
                x_target = max(x_ue, x_g_node_b)
                angular_coefficient_projection = abs((y_g_node_b - y_ue) / (x_g_node_b - x_ue))
                if angular_coefficient_projection > 1:
                    step = step / angular_coefficient_projection  # Reduce the increment on x such that
                    # we sweep y by the original step value thus avoiding missed detections
                while x <= x_target:
                    y = (x - x_ue) / (x_g_node_b - x_ue) * (y_g_node_b - y_ue) + y_ue 
                    for index, machine in enumerate(machines):
                        if machine.x_min <= x <= machine.x_max and machine.y_min <= y <= machine.y_max:
                            z = (y - y_ue) / (y_g_node_b - y_ue) * (z_g_node_b - z_ue) + z_ue
                            # Add height
                            if z <= machine.get_machine_height():
                                is_in_los = False  # Intersection, i.e NLOS
                            # if z <= machine.get_machine_size():
                            #     is_in_los = False  # Intersection, i.e NLOS

                    # Search for the next point 
                    x += step 

            ue.set_los_condition(is_in_los)
