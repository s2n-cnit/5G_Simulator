"""
    Function which computes the uplink BLER characterizing rectangles of an industrial factory
"""
import math
import random

from channel import OFDMChannel
from compute_n_channels import compute_n_channels
from compute_simulator_tick_duration import compute_simulator_tick_duration
from distribution import Distribution
from g_node_b import GNodeB
from geometry import Geometry
from get_modulation_order import get_modulation_order
from instantiate_ues import instantiate_ues
from machine import Machine
from read_data import read_params


def compute_bler(use_case_number: int, factory_length_subdivision: int, factory_width_subdivision: int,
                 g_node_b_x: float, g_node_b_y: float, n_ues: int, payload: int, ue_coordinates_x_y_z_argparse= None):
    """
    Parameters
    --------
        use_case_number : int
            Integer number ranging from 1 to 10 and defining the IIoT use-case according to the 5G-ACIA

        factory_length_subdivision(ls): int
            Integer number used to divide the factory length

        factory_width_subdivision(ws): int
            Integer number used to divide the factory width

        g_node_b_x: float
            x coordinate of the gNB in the factory

        g_node_b_y: float
            y coordinate of the gNB in the factory

        n_ues: int
            Number of UEs to be distributed in the factory

        payload: int
            Number of useful bytes transmitted by UEs

    Return
    ------
        bler_dict : dict
            Dictionary where the keys are the centers of the factory and the values are the corresponding average BLERs

    """
    #  Adding number of iteration to get bler distribution

    n_iter_dist_bler = 1
    n_iterations = 10000  # FIXME: If needed
    bler_dict = dict()
    # Adding required result fo CNIT >> list of dicts

    cnit_results_all = dict()

    # Pick-up inputs
    inputs = read_params('params.yaml')
    machine_size = inputs.get('geometry').get('machine_size')
    # fixme: Add machine height
    machine_height = inputs.get('geometry').get('machine_height')

    inter_machine_distance = inputs.get('geometry').get('inter_machine_distance')
    # TODO: Change the following parameter to use a different approach for UE distribution

    # new distribution is added in yaml file to have only one UE
    ue_distribution = inputs.get('ue').get('ue_spatial_distribution')

    ue_starting_state = inputs.get('ue').get('ue_starting_state')
    g_node_b_starting_state = inputs.get('g_node_b').get('g_node_b_starting_state')
    scheduler_type = inputs.get('simulation').get('scheduling')
    subcarrier_spacing = inputs.get('radio').get('subcarrier_spacing')
    bandwidth = inputs.get('radio').get('bandwidth')
    # added position of machines based on tile number
    init_tile = inputs.get("geometry").get('machine_init_tile')
    end_tile = inputs.get("geometry").get('machine_end_tile')
    tile_list = inputs.get("geometry").get('machine_list_tile')
    machine_list_len = abs(end_tile - init_tile) + 1 + len(tile_list)
    # To run by argparse
    if ue_coordinates_x_y_z_argparse is None:
        ue_coordinates_x_y_z = inputs.get("geometry").get('ue_coordinates_x_y_z')
    else:
        ue_coordinates_x_y_z = ue_coordinates_x_y_z_argparse
        print('ue_coordinates_x_y_z_argparse', ue_coordinates_x_y_z_argparse)
    run_machine_all_tiles = inputs.get("geometry").get('run_machine_all_tiles')

    print(f"init end tiles are: {init_tile} and {end_tile}")
    # Convert the input use-case number to string
    # use-case 11 is not added here !!! , 12 added
    use_case = {1: "Control-to-Control", 2: "Augmented Reality", 3: "Motion Control_Printing Machine",
                4: "Motion Control_Machine Tool", 5: "Motion Control_Packaging Machine",
                6: "Remote Access and Maintenance", 7: "Mobile Control Panels_Assembly Robots",
                8: "Mobile Control Panels_Mobile cranes", 9: "Mobile Robots",
                10: "Closed-Loop Process Control", 12: "fix-ue"}

    if use_case_number in use_case:
        use_case_input = use_case[use_case_number]
        print('The choosen Use Case ', use_case_input, ' is correct.')
    else:
        exit('The input Use Case number is not correct.')

    # Define factory layout
    g = Geometry()
    g.set_use_case(use_case_input)
    factory_length = g.get_factory_dimensions()[0]
    factory_width = g.get_factory_dimensions()[1]
    factory_height = g.get_factory_dimensions()[2]

    # Compute rectangle centers
    rectangle_length = factory_length / factory_length_subdivision
    rectangle_width = factory_width / factory_width_subdivision

    # Check that subdivisions are integer multiples of factory length and factory width
    # if factory_length % factory_length_subdivision != 0 or factory_length % factory_length_subdivision != 0 \
    #         or rectangle_length < 1 or rectangle_width < 1:
    if factory_length % factory_length_subdivision != 0 or factory_width % factory_width_subdivision != 0 \
            or rectangle_length < 1 or rectangle_width < 1:
        exit('Check the factory_length_subdivision and or factory_width_subdivision parameter,'
             'they do not allow to have a precise subdivision of the factory in rectangles')

    # Compute the rectangle centers
    for x in range(factory_length_subdivision):
        for y in range(factory_width_subdivision):
            rectangle_center = (rectangle_length / 2 + rectangle_length * x, rectangle_width / 2 + rectangle_width * y)
            bler_dict[rectangle_center] = 0  # Initialization
    # Adjust the input machine size and inter machine distance in case they are not compatible with the factory layout
    g.set_machine_size(factory_length, factory_width, factory_height, machine_size, inter_machine_distance)
    machine_size = g.get_machine_size()
    inter_machine_distance = g.get_inter_machine_distance()

    # Add loop for changing machines tiles

    for each_loop in range(len(bler_dict)):  # len(bler_dict) = total number of tiles -200 for test smaller loop
        cnit_results = dict()  # create results for each run
        # Initialize environment
        # here in Distribution I changed the number of machines on x , y to 1
        # I add another parameter for number of machines (machine_list_len) , machine height
        d = Distribution(use_case=use_case_input, factory_length=factory_length, factory_width=factory_width,
                         ue_distribution=ue_distribution, machine_size=machine_size,
                         inter_machine_distance=inter_machine_distance, machine_list_len=machine_list_len,
                         machine_height=machine_height)

        # Instantiate machines, i.e. obstacles for the communication perspective
        # Distribute machines in the factory
        # now one machine is located in x[0],y[0] , Can I add a loop to change the position of
        #  the machine each time
        # following loop will plot all machine at the same time (multiple machines)
        x_y_coordinates = list(bler_dict.keys())
        machine_tile_x_ls = []
        machine_tile_y_ls = []
        # Add another loop for run machine in all tiles separately
        if run_machine_all_tiles:
            if inputs.get("geometry").get('machine_distribution') == 1:
                tile_number = each_loop
                machine_tile_x = x_y_coordinates[tile_number][0]
                machine_tile_y = x_y_coordinates[tile_number][1]
                machine_tile_x_ls.append(machine_tile_x)
                machine_tile_y_ls.append(machine_tile_y)
                print(f"compute_bler: >>> machine_tile_x list is: {machine_tile_x_ls} and "
                      f"machine_tile_x {machine_tile_y_ls}")
                # re-define machine array + machine height
                machine_array = [Machine(machine_size, d.get_ue_density(), machine_height) for i in
                                 range(len(machine_tile_x_ls))]
                d.distribute_selective_machines(machine_array, machine_tile_x_ls=machine_tile_x_ls,
                                                machine_tile_y_ls=machine_tile_y_ls)

            else:
                machine_array = [Machine(machine_size, d.get_ue_density(), machine_height) for i in
                                 range(d.get_number_of_machines())]
                print(f'Compute_bler >>> ue density is: {d.get_ue_density()} '
                      f'and machine array len is {len(machine_array)}')
                d.distribute_machines(machine_array)
            print(f"Bler>>>> get number of machines : {d.get_number_of_machines()}")
        else:
            print("Else is running")
            if inputs.get("geometry").get('machine_distribution') == 1:
                for i in range(init_tile, end_tile + 1):
                    machine_tile_x = x_y_coordinates[i][0]
                    machine_tile_y = x_y_coordinates[i][1]
                    machine_tile_x_ls.append(machine_tile_x)
                    machine_tile_y_ls.append(machine_tile_y)
                for i in tile_list:
                    machine_tile_x = x_y_coordinates[i][0]
                    machine_tile_y = x_y_coordinates[i][1]
                    machine_tile_x_ls.append(machine_tile_x)
                    machine_tile_y_ls.append(machine_tile_y)
                    print(f'compute_bler: machine tiles x , y are {machine_tile_x} and {machine_tile_y}')
                print(f">>> compute_bler: >>> machine_tile_x list is: {machine_tile_x_ls} and "
                      f"machine_tile_x {machine_tile_y_ls}")
                # re-define machine array
                machine_array = [Machine(machine_size, d.get_ue_density()) for i in range(len(machine_tile_x_ls))]
                d.distribute_selective_machines(machine_array, machine_tile_x_ls=machine_tile_x_ls,
                                                machine_tile_y_ls=machine_tile_y_ls)
                # cnit_results['machines_list']= {"x_coor":machine_tile_x_ls,"y_coor":machine_tile_y_ls }
                # cnit_results['machines_list']= f"({machine_tile_x_ls},{machine_tile_y_ls})"

            else:
                machine_array = [Machine(machine_size, d.get_ue_density()) for i in range(d.get_number_of_machines())]
                print(f'Compute_bler >>> ue density is: {d.get_ue_density()} '
                      f'and machine array len is {len(machine_array)}')
                d.distribute_machines(machine_array)
            print(f"Bler>>>> get number of machines : {d.get_number_of_machines()}")

        cnit_results['machines_list'] = {"x_coor": machine_tile_x_ls, "y_coor": machine_tile_y_ls}
        print(cnit_results['machines_list'])
        cnit_results['machine_height'] = str(machine_height)
        # Instantiate UEs
        simulator_tick_duration, ofdm_symbol_duration = compute_simulator_tick_duration(input_params_dict=inputs)
        ue_list = instantiate_ues(input_params_dict=inputs, tot_number_of_ues=n_ues, starting_state=ue_starting_state,
                                  simulator_tick_duration=simulator_tick_duration)

        # Find maximum machine size, if any
        max_machine_size = machine_array[0].get_machine_size()
        for machine in machine_array:
            new_machine_size = machine.get_machine_size()
            if new_machine_size > max_machine_size:
                max_machine_size = new_machine_size

        # Distribute UEs in the factory
        # Fix the positions of ues  (bler_dict has all center coordinates)
        if ue_distribution == 'tile_center':
            # x_y_coordinates = list(bler_dict.keys()) #  I already defined in the top
            # print(f">>>>>>>>>> x_y_Cordinates are {x_y_coordinates[0:len(ue_list)]}")
            for index, ue in enumerate(ue_list):
                x_coordinate = ue_coordinates_x_y_z[0]
                print(f">>>>>>>>>>>> ue X_Coordinate is : {x_coordinate}")
                y_coordinate = ue_coordinates_x_y_z[1]
                print(f">>>>>>>>>>>> ue Y_Coordinate is : {y_coordinate}")
                z_coordinate = ue_coordinates_x_y_z[2]
                ue.set_coordinates(x_coordinate, y_coordinate,
                                   z_coordinate)  # z values should consider fixed to machine size
            cnit_results['ue_coordinate'] = ue_coordinates_x_y_z
        elif ue_distribution == 'Uniform':
            for ue in ue_list:
                ue.set_coordinates(random.uniform(0, factory_length), random.uniform(0, factory_width),
                                   random.uniform(0, max_machine_size))
        elif ue_distribution == 'Uniform_Guaranteed':
            if len(ue_list) < len(bler_dict):
                exit('This UE distribution on this scenario needs more UEs.')
            for rectangle_center in bler_dict.keys():
                ue = next((unset_ue for unset_ue in ue_list if unset_ue.get_coordinates() == (0.0, 0.0, 0.0)), None)
                if ue is not None:
                    ue.set_coordinates(random.uniform(rectangle_center[0] - rectangle_length / 2,
                                                      rectangle_center[0] + rectangle_length / 2),
                                       random.uniform(rectangle_center[1] - rectangle_width / 2,
                                                      rectangle_center[1] + rectangle_width / 2),
                                       random.uniform(0, max_machine_size))

            while (ue := next((unset_ue for unset_ue in ue_list if unset_ue.get_coordinates() == (0.0, 0.0, 0.0)),
                              None)) is not None:
                ue.set_coordinates(random.uniform(0, factory_length), random.uniform(0, factory_width),
                                   random.uniform(0, max_machine_size))
        else:
            exit('The UE distribution statistics is not recognized')

        # Instantiate the channel
        n_channels = compute_n_channels(inputs)
        channel = OFDMChannel(params=inputs, n_channels=n_channels, factory_height=factory_height)

        # Instantiate the gNB and the corresponding scheduler
        g_node_b = GNodeB(params=inputs, n_channels=n_channels, ues_list=ue_list,
                          starting_state=g_node_b_starting_state)

        # Distribute the gNB in the factory
        g_node_b_z = factory_height
        if 0 <= g_node_b_x <= factory_length and 0 <= g_node_b_y <= factory_width:
            d.distribute_g_node_b(g_node_bs=g_node_b, x=g_node_b_x, y=g_node_b_y, z=g_node_b_z)
        else:
            exit('The gNB coordinates are not suitable for the input use-case, check geometry features')

        # Assign LOS and NLOS condition to UEs
        d.are_ues_in_los(ue_list=ue_list, g_node_b=g_node_b, machines=machine_array)

        # Compute distances between UEs and gNB
        g.set_ue_g_node_b_distances(ue_list=ue_list, g_node_b=g_node_b)

        # Compute BLER for each UE
        bler_list = list()
        bler_dist_lst = list()
        bler_dist_lst_each_ue = list()
        # for ue in ue_list:
        for index, ue in enumerate(ue_list):
            # add another loop to compute bler distribution bler_dist_lst
            for iter_dist in range(n_iter_dist_bler + 1):
                bler = 0
                for iteration in range(n_iterations + 1):  # n_iteration = 10000
                    is_received, snr_db = channel.is_received(ue=ue, g_node_b=g_node_b,
                                                              tx_rx_distance=ue.get_distance_from_g_node_b(),
                                                              link_direction="uplink")
                    modulation_order = get_modulation_order(scheduler_type=scheduler_type, snr_db=snr_db)
                    modulation_order_ask = math.sqrt(modulation_order)
                    n_bits_per_subcarrier = math.log2(modulation_order)
                    n_subcarriers = payload * 8 / n_bits_per_subcarrier
                    bit_rate = n_subcarriers * n_bits_per_subcarrier * subcarrier_spacing * 1e3
                    snr = pow(10, snr_db / 10)
                    eb_n0 = snr * bandwidth * 1e9 / bit_rate
                    bit_error_probability = \
                        (modulation_order_ask - 1) / (
                                modulation_order_ask * math.log2(modulation_order_ask)) * math.erfc(
                            math.sqrt(eb_n0 * 3 * math.log2(modulation_order_ask) / (pow(modulation_order_ask, 2) - 1)))
                    bler += 1 - pow(1 - bit_error_probability, payload * 8)
                bler = bler / (n_iterations + 1)
                bler_dist_lst.append(bler)
            bler_dist_lst_each_ue.append(bler_dist_lst)
            bler_list.append(bler)
            """
            print('BLER {} per UE {} with coordinates ({}, {})'.format(bler, ue.get_ue_id(), ue.get_coordinates()[0],
                                                               ue.get_coordinates()[1]))
            """

        # modify to run for one UE > now its running for all rects >>> I removed indentation of the ploting !
        # write new for-loop to navigate over machines
        #
        # Group UEs per rectangle and compute the corresponding average BLER
        for key, bler_value in bler_dict.items():
            x_rectangle = key[0]
            y_rectangle = key[1]
            ue_counter = 0
            for index, ue in enumerate(ue_list):
                x_ue, y_ue, z_ue = ue.get_coordinates()
                if x_rectangle - rectangle_length / 2 <= x_ue <= x_rectangle + rectangle_length / 2 and y_rectangle - \
                        rectangle_width / 2 <= y_ue <= y_rectangle + rectangle_width / 2:
                    bler_value += bler_list[index]
                    print("*************************************************************************")
                    print(
                        f" user is in rectangle ({x_rectangle}, {y_rectangle}), bler index and value are {index} {bler_list[index]}")
                    cnit_results['bler_ue'] = {f"({x_rectangle}, {y_rectangle})": f"{bler_list[index]}"}
                    # Add bler_dist
                    cnit_results['bler_ue_dist'] = {
                        f"({x_rectangle}, {y_rectangle})": f"{bler_dist_lst_each_ue[index]}"}
                    ue_counter += 1
            if ue_counter != 0:
                bler_dict[key] = bler_value / ue_counter
            else:
                bler_dict[key] = None
            # print('Rectangle center ({}, {}), with {} UEs, BLER = {}'.format(x_rectangle, y_rectangle, ue_counter,
            #                                                                  bler_dict[key]))

        # create a dict of results for each tile
        # cnit_results['bler_dict'] = str(bler_dict) # No need to save NONE values for one ue
        for index, ue in enumerate(ue_list):
            print('UE number {} with coordinates ({},{},{}) is connected to gNB{}: {} '
                  'with distance {} m'.format(ue.get_ue_id(), ue.x, ue.y, ue.z, [g_node_b_x, g_node_b_y] ,ue.get_los_condition(),
                                              ue.get_distance_from_g_node_b()))
            cnit_results["LOS_conditions"] = str(ue.get_los_condition())
            cnit_results["distance_from_gnb"] = (ue.get_distance_from_g_node_b())
            print(cnit_results["LOS_conditions"])
        cnit_results['factory_size'] = [factory_length, factory_width, factory_height]
        # Test part for dic and bler_list
        # for key, bler_value in bler_dict.items():
        #     x_rectangle = key[0]
        #     y_rectangle = key[1]
        #     for index, ue in enumerate(ue_list):
        #         x_ue, y_ue, z_ue = ue.get_coordinates()
        #         # print (f"print >>>>ue cordinates are: {x_ue}, {y_ue}, {z_ue}")
        #         if x_rectangle - rectangle_length/2 <= x_ue <= x_rectangle + rectangle_length/2 and y_rectangle - \
        #                 rectangle_width / 2 <= y_ue <= y_rectangle + rectangle_width / 2:
        #             print ("*************************************************************************")
        #             print(f" user is in rectangle ({x_rectangle}, {y_rectangle}), bler index and value are {index} {bler_list[index]}")

        #
        # for index, ue in enumerate(ue_list):
        #     print(f" Compute_bler>>>>> ue.bler are {bler_list[index]}")

        """
        # 3D PLOT OF THE FACTORY (gNB + UEs + MACHINES + JOINING LINES BETWEEN UEs and gNB)
        # deindent the plot to run for one ue only

            # Print coordinates and plot the result
        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')

        # Set axis limit
        ax.set_xlim([0, factory_length])
        # ax.set_xlim([0, factory_width])
        ax.set_ylim([0, factory_width])
        ax.set_zlim([0, factory_height])

        # Machine plot
        for i in range(d.get_number_of_machines()):
            print('x = ' + str(machine_array[i].get_coordinates()[0]) + ', y = ' + str(
                machine_array[i].get_coordinates()[1]))
            legend1 = ax.scatter(machine_array[i].x, machine_array[i].y, machine_array[i].z, color='gray')
            machine_size = machine_array[i].get_machine_size()
            plt.plot([machine_array[i].x - machine_size / 2, machine_array[i].x + machine_size / 2],
                     [machine_array[i].y - machine_size / 2, machine_array[i].y - machine_size / 2],
                     [machine_array[i].z - machine_size / 2, machine_array[i].z - machine_size / 2], color='gray')
            plt.plot([machine_array[i].x - machine_size / 2, machine_array[i].x - machine_size / 2],
                     [machine_array[i].y - machine_size / 2, machine_array[i].y - machine_size / 2],
                     [machine_array[i].z - machine_size / 2, machine_array[i].z + machine_size / 2], color='gray')
            plt.plot([machine_array[i].x - machine_size / 2, machine_array[i].x + machine_size / 2],
                     [machine_array[i].y - machine_size / 2, machine_array[i].y - machine_size / 2],
                     [machine_array[i].z + machine_size / 2, machine_array[i].z + machine_size / 2], color='gray')
            plt.plot([machine_array[i].x + machine_size / 2, machine_array[i].x + machine_size / 2],
                     [machine_array[i].y - machine_size / 2, machine_array[i].y - machine_size / 2],
                     [machine_array[i].z + machine_size / 2, machine_array[i].z - machine_size / 2], color='gray')
            plt.plot([machine_array[i].x - machine_size / 2, machine_array[i].x - machine_size / 2],
                     [machine_array[i].y - machine_size / 2, machine_array[i].y + machine_size / 2],
                     [machine_array[i].z - machine_size / 2, machine_array[i].z - machine_size / 2], color='gray')
            plt.plot([machine_array[i].x + machine_size / 2, machine_array[i].x + machine_size / 2],
                     [machine_array[i].y - machine_size / 2, machine_array[i].y + machine_size / 2],
                     [machine_array[i].z - machine_size / 2, machine_array[i].z - machine_size / 2], color='gray')
            plt.plot([machine_array[i].x - machine_size / 2, machine_array[i].x + machine_size / 2],
                     [machine_array[i].y + machine_size / 2, machine_array[i].y + machine_size / 2],
                     [machine_array[i].z - machine_size / 2, machine_array[i].z - machine_size / 2], color='gray')
            plt.plot([machine_array[i].x - machine_size / 2, machine_array[i].x - machine_size / 2],
                     [machine_array[i].y + machine_size / 2, machine_array[i].y + machine_size / 2],
                     [machine_array[i].z - machine_size / 2, machine_array[i].z + machine_size / 2], color='gray')
            plt.plot([machine_array[i].x + machine_size / 2, machine_array[i].x + machine_size / 2],
                     [machine_array[i].y + machine_size / 2, machine_array[i].y + machine_size / 2],
                     [machine_array[i].z - machine_size / 2, machine_array[i].z + machine_size / 2], color='gray')
            plt.plot([machine_array[i].x - machine_size / 2, machine_array[i].x + machine_size / 2],
                     [machine_array[i].y + machine_size / 2, machine_array[i].y + machine_size / 2],
                     [machine_array[i].z + machine_size / 2, machine_array[i].z + machine_size / 2], color='gray')
            plt.plot([machine_array[i].x + machine_size / 2, machine_array[i].x + machine_size / 2],
                     [machine_array[i].y - machine_size / 2, machine_array[i].y + machine_size / 2],
                     [machine_array[i].z + machine_size / 2, machine_array[i].z + machine_size / 2], color='gray')
            plt.plot([machine_array[i].x - machine_size / 2, machine_array[i].x - machine_size / 2],
                     [machine_array[i].y - machine_size / 2, machine_array[i].y + machine_size / 2],
                     [machine_array[i].z + machine_size / 2, machine_array[i].z + machine_size / 2], color='gray')

        # UE plot
        for index, ue in enumerate(ue_list):
            print(f"Compute_bler_plot>>>> len of ue_list is: {len(ue_list)}")
            legend2 = ax.scatter(ue.x, ue.y, ue.z, color='red')

        # gNB plot
        legend3 = ax.scatter(g_node_b.x, g_node_b.y, g_node_b.z, color='blue', marker="^")  # , s=100)

            # Joining line plot
        for index, ue in enumerate(ue_list):
            plt.plot([ue.x, g_node_b.x], [ue.y, g_node_b.y], [ue.z, g_node_b.z], color='black')
            print('UE number {} with coordinates ({},{},{}) is connected to gNB: {} '
                  'with distance {} m'.format(ue.get_ue_id(), ue.x, ue.y, ue.z, ue.get_los_condition(),
                                              ue.get_distance_from_g_node_b()))
            cnit_results["LOS_conditions"] = str(ue.get_los_condition())
            print(cnit_results["LOS_conditions"])

        print('*****************************************************************')
            # #
        plt.title('Factory layout')
        plt.xlabel('Factory length [m]')
        plt.ylabel('Factory width [m]')
        ax.set_zlabel('Factory height [m]')
        plt.legend((legend1, legend2, legend3), ('Machine Center', 'UE', 'gNB'))
        plt.show()
        """
        # create final dict for each tile
        cnit_results_all[f"tile_{each_loop}"] = cnit_results
    return bler_dict, cnit_results_all
