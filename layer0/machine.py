import math
import sys


class Machine:
    """
        Class for machines in the system

    Attributes
    ----------
    machine_size : int
        ! TODO what does it represent ?
    ue_density : float
        UE spatial density, used to attach devices to the machine.

    """
    def __init__(self, machine_size: int = None, ue_density: float = None, machine_height: int = 3):

        # Center_coordinates
        self.x = 0
        self.y = 0
        self.z = 0

        # Coordinates of the area boundary 
        self.x_max = 0
        self.x_min = 0
        self.y_max = 0
        self.y_min = 0
        if machine_size is not None and ue_density is not None:
            self.machine_size = machine_size
            self.machine_height = machine_height

            # changed to 1 for max number ue for each machine
            # self.max_number_of_ues = 1
            self.max_number_of_ues = math.ceil(ue_density * (self.machine_size**3))
            print(f'Machine class>> max_number_of_ues attached to a machine: {self.max_number_of_ues}')
            # now = 0 >>>ue_density = 0 for selected uc 12

        else:  # bi-rex case
            self.machine_size = 0  # it will be set afterwards
            self.max_number_of_ues = 0  # it will be set afterwards

        # changed to 1 for number of ue for each machine
        self.number_of_ues = 1
        # self.number_of_ues = 0

    def set_coordinates(self, x_input, y_input, z_input):
        self.x = x_input
        self.y = y_input
        self.z = z_input

    def get_coordinates(self):
        return self.x, self.y, self.z

    def get_machine_size(self):
        return self.machine_size

    def set_machine_size(self, machine_size: int):
        self.machine_size = machine_size

    def set_max_number_of_ues(self, max_number_of_ues: int):
        self.max_number_of_ues = max_number_of_ues

    def get_max_number_of_ues(self):
        return self.max_number_of_ues

    # Add machine height function (I  add machine height to machine class)
    def get_machine_height(self):
        return  self.machine_height

    def add_new_ue(self):
        if self.number_of_ues+1 <= self.max_number_of_ues:
            self.number_of_ues += 1
        else:
            return sys.exit("You are trying to add a new UE but the current machine is already full!")  # FIXME
    
    def get_number_of_ues(self):
        return self.number_of_ues
