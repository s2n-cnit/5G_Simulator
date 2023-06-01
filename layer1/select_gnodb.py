from numpy import zeros


def select_gnodb(series: list, gnodb_postion_lst: list, machine_tile_lst: list):
    """
    param: list of high bler tiles of gnodbs
    """
    # Comparing each serie with the rest of the series
    correlated_gnodbs_coor = []
    correlated_gnodbs_id = []
    correlated_gnodbs_coor_set = dict()
    correlated_gnodbs_id_set = dict()

    intersect_lst = zeros([len(series), len(series)], dtype=list)
    '''
     NOTE: Code for upper matrix
    '''
    # index_serie = 0
    # while index_serie < len(series) - 1:
    #     sub_index = index_serie + 1
    #     while sub_index < len(series):
    #         # print(f"comparing {index_serie} with {sub_index}")
    #         intersect_lst[index_serie, sub_index] = [value for value in series[index_serie] if
    #                                                  value in series[sub_index]]
    #         if machine_tile in intersect_lst[index_serie][sub_index]:
    #             print(
    #                 f"For the machine in tile {machine_tile} gNodeB {gnodb_position_lst[index_serie]} and {gnodb_position_lst[sub_index]} are correlated ")
    #             correlated_gnodbs.append([index_serie, sub_index])
    #         sub_index += 1
    #
    #     index_serie += 1

    # fixme: code for creation of a full matrix with the diagonal values
    for i in range(len(series)):
        # print (i)
        correlated_gnodbs_id_set[i] = set()
        for j in range(len(series)):
            intersect_lst[i][j] = [value for value in series[i] if value in series[j]]

            for machine_tile in machine_tile_lst:
                if machine_tile in intersect_lst[i][j]:
                    # print(
                    #     f"For the machine in tile {machine_tile} gNodeB {gnodb_position_lst[i]} and {gnodb_position_lst[j]} are correlated ")
                    correlated_gnodbs_coor.append([gnodb_postion_lst[i], gnodb_postion_lst[j]])
                    correlated_gnodbs_id.append([i, j])
                    correlated_gnodbs_id_set[i].add(i)
                    correlated_gnodbs_id_set[i].add(j)
    print(f'correlated_gnodbs_id_set is: {correlated_gnodbs_id_set}')
    print(f'correlated gnobs for the machine located in tile {machine_tile_lst[0]} ... are {correlated_gnodbs_id}')
    # print(f"intersect matrix is {intersect_lst.shape}\n : {intersect_lst}")
    # with open('corr_set')
    return intersect_lst, correlated_gnodbs_coor, correlated_gnodbs_id, correlated_gnodbs_id_set
