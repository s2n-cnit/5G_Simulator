import numpy as np


def create_bler_list(parameters: dict):
    '''
    :param parameters: input dictionary
    :return: extract bler list, high_bler_tile number lst
    '''
    bler_list = np.zeros(len(parameters.keys()))
    # print("len(parameters.keys())",len(parameters.keys()))
    # TODO: make class to have also tile position(now I used another function!)
    high_bler_tile_number_lst = []
    machine_position = []

    for tile, tile_info in parameters.items():
        temp = tile.split("_")
        tile_number = int(temp[1])
        temp_all_bler = tile_info["bler_ue"]

        for key2, value2 in temp_all_bler.items():
            if tile_info['LOS_conditions'] == "False":
                # temp_all_bler[key2] = 1  # this is bler =1 in the case of nlos
                bler_list[tile_number] = np.float16(temp_all_bler[key2])
                high_bler_tile_number_lst.append(tile_number)

                # print(tile_number)
            else:
                bler_list[tile_number] = np.float16(value2)

    return bler_list, high_bler_tile_number_lst
