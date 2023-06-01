def get_tile_coordinates(parameters: dict, ue_coor ):
    '''
    :param parameters: input dictionary
    :return: bler list
    '''
    x_ue = int(ue_coor[0])
    y_ue = int(ue_coor[1])
    tile_position_list = []
    for tile, tile_info in parameters.items():
        temp = tile.split("_")
        tile_number = int(temp[1])
        temp_all_bler = tile_info["machines_list"]
        x = temp_all_bler['x_coor'][0]
        y = temp_all_bler['y_coor'][0]
        #     print (int(x_ue), int(y_ue))
        if int(x_ue) % 2 == 0:
            x_ue += 1
        if int(y_ue) % 2 == 0:
            y_ue += 1
        if int(x) == x_ue:
            if int(y) == y_ue:
                ue_tile_number = tile_number

        tile_position_list.append([x, y])
    # print(f"Tile postion list len is{len(tile_position_list)} : {(tile_position_list)}")
    return tile_position_list, ue_tile_number
