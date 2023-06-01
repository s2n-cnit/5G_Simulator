import json
import os

from create_bler_list import create_bler_list


def read_json_files(path_to_dir='', ue_dir='ue_x1_y1',
                    gnob_lst=[[1, 25, 50, 75, 100], [1, 25, 50, 75, 100]]):
    temp = ue_dir.split("_")
    x_ = temp[1]
    y_ = temp[2]
    ue_x_coor = int(x_[1:])
    ue_y_coor = int(y_[1:])
    ue_coor = [ue_x_coor, ue_y_coor]
    # Reading data
    parameters_dict = dict()
    gnodbs_cor_dict = dict()
    all_bler_value_dict = dict()
    all_high_bler_tile_number_dict = dict()
    # for x in [1, 25, 50, 75, 100]:
    #     for y in [1, 25, 50, 75, 100]:
    for x in gnob_lst[0]:
        for y in gnob_lst[1]:
            complete_path = os.path.join(path_to_dir, ue_dir, f"bs_uc12_ls50_ws50_x{x}_y{y}_n1_p50_cnit.json")
            # with open(f"{path_to_dir}/{ue_dir}/bs_uc12_ls50_ws50_x{x}_y{y}_n1_p50_cnit.json") as f:
            with open(complete_path) as f:
                parameters_dict[f"parameters_{x}_{y}"] = json.load(f)
                # globals()[f"parameters_{x}_{y}"] = json.load(f)  # x,y_gnodB = [1,75] z=10
                # param_lst.append(globals()[f"parameters_{x}_{y}"])
            # gnodbs_dict[f"gnodb_{x}_{y}"] = [x, y, 10]
            gnodbs_cor_dict[f"gnodb_{x}_{y}"] = [x, y]
            all_bler_value_dict[f"gnodb_{x}_{y}"] = create_bler_list(parameters_dict[f"parameters_{x}_{y}"])[0]
            all_high_bler_tile_number_dict[f"gnodb_{x}_{y}"] = create_bler_list(parameters_dict[f"parameters_{x}_{y}"])[
                1]
            # globals()[f"gnodb_{x}_{y}"] = [x,y,10]

    return parameters_dict, gnodbs_cor_dict, all_bler_value_dict, all_high_bler_tile_number_dict, ue_coor

#
# parameters_dict, gnodbs_dict, all_bler_dict, all_high_bler_tile_number_lst, ue_coor = read_json_files(ue_dir='ue_x1_y1')
# gnodb_position_lst = [values for key, values in gnodbs_dict.items()]
#
# print(len(gnodb_position_lst))
# print((gnodbs_dict))
