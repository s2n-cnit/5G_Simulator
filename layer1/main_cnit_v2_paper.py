import json
import numpy as np
import pandas as pd
from create_algos_data import create_algos_data
from create_time_serie import create_time_serie
from find_correlation import find_correlation
from get_tile_coordinates import get_tile_coordinates
from gnodb_plot import gnodb_plot
from select_gnodb import select_gnodb
from sig_plot import sig_plot
from square_path import square_path
from read_json_files import read_json_files # the json files generated from layer0
import os
from pathlib import Path

# set the ue dir for the json files generated by layer0 
# in the Gui version it became dynamic
# ue_dir = 'ue_x75_y99'
# ue_dir = 'ue_x51_y31'
# ue_dir_lst =['ue_x1_y1', 'ue_x3_y1','ue_x5_y1','ue_x7_y1','ue_x9_y1','ue_x11_y1','ue_x13_y1',
#              'ue_x15_y1','ue_x17_y1','ue_x17_y3', 'ue_x17_y5', 'ue_x15_y5', 'ue_x13_y5', 'ue_x11_y5',
#              'ue_x9_y5', 'ue_x7_y5', 'ue_x5_y5', 'ue_x3_y5', 'ue_x1_y5', 'ue_x1_y3',]#
# ue_dir_lst =['ue_x1_y1', 'ue_x3_y1','ue_x5_y1','ue_x7_y1','ue_x9_y1','ue_x11_y1','ue_x13_y1',
#              'ue_x15_y1','ue_x17_y1','ue_x17_y3', 'ue_x17_y5', 'ue_x15_y5', 'ue_x13_y5', 'ue_x11_y5',
#              'ue_x9_y5', 'ue_x7_y5', 'ue_x5_y5', 'ue_x3_y5', 'ue_x1_y5', 'ue_x1_y3']
# ue_dir_lst = ['ue_x1_y1']

# paper ue path
x25_y1to27_dir = [f'ue_x25_y{i}' for i in range(1, 28, 2)]
parent_path = Path(os.getcwd())
paths = os.path.join(parent_path, 'data_ue_paths', "path_601_0_14")
ue_dir_lst = x25_y1to27_dir

ue_config_algo_opt = set()
ue_config = set()
final_results = dict()
ue_square_bler_details = dict()

for ue_dir in ue_dir_lst:
    # Reading data
    # parameters_dict, gnodbs_dict, all_bler_dict, all_high_bler_tile_number_dict, ue_coor \
    #     = read_json_files(ue_dir=ue_dir)

    # for paper
    parameters_dict, gnodbs_dict, all_bler_dict, all_high_bler_tile_number_dict, ue_coor \
        = read_json_files(path_to_dir=paths, ue_dir=ue_dir)

    all_bler_list = list(all_bler_dict.values())
    all_high_bler_tile_number_lst = list(all_high_bler_tile_number_dict.values())
    gnodb_postion_lst = [values for key, values in gnodbs_dict.items()]
    tile_postion_list, ue_tile_number = get_tile_coordinates(parameters_dict["parameters_25_25"], ue_coor=ue_coor)

    # TODO: add new correlation function to the path and all
    corr_coeff_rows, corr_coef_1lst, corr_row_by_row = find_correlation(all_bler_dict["gnodb_75_75"],
                                                                        all_bler_dict["gnodb_25_25"],
                                                                        tile_postion_list, plotting=False, threed=False)

    ######################## Correlation for repeated serie ####################
    repeated_blers = create_time_serie(gnodb_postion_lst=gnodb_postion_lst, serie=all_bler_list, plotting=True,
                                       ue_dir=f"{ue_coor + [10]}")
    
    ##########################################################################
    # select the best gnob based on the position of the machine and gnobs locations
    intersect_list, correlated_gnodbs_coor, correlated_gnodbs_id, correlated_gnodbs_id_set = select_gnodb(
        all_high_bler_tile_number_lst,
        gnodb_postion_lst, machine_tile_lst=[5])

    # plotting
    sig_plot(first_serie=all_bler_dict["gnodb_25_100"],
             second_serie=all_bler_dict["gnodb_100_75"],
             tile_postion_list=tile_postion_list, first_gnodb=gnodbs_dict["gnodb_50_100"],
             second_gnodb=gnodbs_dict["gnodb_100_75"], threed=True)

    sig_plot(first_serie=all_bler_dict["gnodb_50_50"],
             second_serie=all_bler_dict["gnodb_50_75"],
             tile_postion_list=tile_postion_list, first_gnodb=gnodbs_dict["gnodb_50_50"],
             second_gnodb=gnodbs_dict["gnodb_50_75"], threed=True)

    # #################################### Generate path for machine #################################
    # get path direction
    # up_range, right_top_range, right_bot_range, left_bot_range = square_path(width_of_square=30, height_of_square=25,
    #                                                                          start_tile=120)  # default is 30
    # Paper machine path ====================================================================================
    # up_range, right_top_range, right_bot_range, left_bot_range = square_path(width_of_square=20, height_of_square=20,
    #                                                                          start_tile=5)  # default is 30
    up_range, right_top_range, right_bot_range, left_bot_range = square_path(width_of_square=35, height_of_square=25,
                                                                             start_tile=608)  # default is 30
    # Paper machine path END ====================================================================================

    print("##################### print Path ###########################")
    sq_tiles_lst = up_range + right_top_range + right_bot_range + left_bot_range

    # paper one tile
    # sq_tiles_lst = [611, 612, 613, 614, 615, 616, 617, 618, 619, 620]
    sq_tiles_lst = [110]

    # plot
    sig_plot(tile_postion_list=tile_postion_list, threed=None, path_plot=True, sq_tiles_lst=sq_tiles_lst)

    ##########################################################################
    # fixme: TEST
    # select the best gnob based on the position of the machine path and gnobs locations
    print(f'#########################################TEST part for finding geo')
    sq_tiles_corr_gnodbid_lst = list()

    # Now extract path tiles from each gnob blers
    sq_blers_dict = dict()
    index = 0
    for key, value in gnodbs_dict.items():
        sq_blers_dict[key] = [all_bler_list[index][i] for i in sq_tiles_lst]
        index += 1
    all_sq_blers = list(sq_blers_dict.values())
    details = []
    i=0
    for gnodeb in all_sq_blers:
        details.append(
            {
            f'gnodeb{i}_max_blers': max(all_sq_blers),
            f'gnodeb{i}_min_blers': min(all_sq_blers),
            f'gnodeb{i}_mean_blers': np.mean(all_sq_blers),
            }
        )
        i += 1
    ue_square_bler_details[f'{ue_dir}'] = details
    print("=============================== BLER DICT=============================================\n", sq_blers_dict)

    print("#########################################################################")
    # ===============================================================================================================
    # select nominated gnodebs to show
    selected_gnodeb_to_show = [
        'gnodb_25_25', 'gnodb_25_50','gnodb_25_75',
        'gnodb_75_25', 'gnodb_75_50', 'gnodb_75_75'
    ]
    selected_square_blers_values = {key : value for key, value in sq_blers_dict.items()
                                    if key in selected_gnodeb_to_show
                                    }
    # re-assign for paper
    gnodb_postion_lst_paper = [values for key, values in gnodbs_dict.items()
                         if key in selected_gnodeb_to_show
                         ]
    all_sq_blers_guass_rep = create_time_serie(gnodb_postion_lst=gnodb_postion_lst_paper,
                                               serie=selected_square_blers_values.values(),
                                               type_rand='Guassian', plotting=True, ue_dir=f"{ue_coor + [0]}")
    
    # ########################################### gNodBs plot ###########################################
    gnodb_plot(gnodb_postion_lst_paper, tile_postion_list, ue=ue_coor, machine_tile=610, machine_3d=True)

    # ===============================================================================================================
    # Uncomment to show the figure of BLER for the time series of all gNodeBs
    # all_sq_blers_guass_rep = create_time_serie(gnodb_postion_lst=gnodb_postion_lst, serie=all_sq_blers,
    #                                            type_rand='Guassian', plotting=True, ue_dir=f"{ue_coor + [0]}")

    # create sets from square path
    intersect_list_sq, correlated_gnodbs_coor_sq, correlated_gnodbs_id_sq, correlated_gnodbs_id_set_sq = select_gnodb(
        all_high_bler_tile_number_lst,
        gnodb_postion_lst, machine_tile_lst=sq_tiles_lst)

    # ################ Find Corr bw random sq_repeated_series########################################################
    sq_calculated_corr_coef_1lst = list()
    for num1, serie1 in enumerate(all_sq_blers_guass_rep):
        for num2, serie2 in enumerate(all_sq_blers_guass_rep):
            corr_coef = np.corrcoef(serie1, serie2)
            sq_calculated_corr_coef_1lst.append(corr_coef)
            print(f"Correlation coeff for sq_gnodb {num1} and sq_gnodb {num2} is : {corr_coef}")
    # #################################################################################################################
    # create data frame to depict better
    df = pd.DataFrame(corr_coeff_rows)
    with open("corr_row_by_row_xy100_100_50_50.json", 'w') as f:
        json.dump(str(corr_row_by_row), f)
    df.to_csv('corr_coef_rows.xlsx')
    print(df)

    # conv_two = np.convolve(results[0], results[1])
    # conv_two2 = np.convolve(results[2], results[7], 'same')
    # print(output_sq_path[ue_dir])
    # sig_plot(conv_two)
    # sig_plot(conv_two2)

    # run step by step for each ue postion===============
    # Comment the following to run withour question untill the end
    cont = input(" Continue y/n: ")
    if cont.capitalize() == 'N':
        break


for key, value in ue_square_bler_details.items():
    print(key, " : ", value)
# Write in a csv file for layer 3 which is not proposed in this version
# with open('ue_final_results_algos.csv', 'w') as f:
#     for key in final_results.keys():
#         f.write(f"{key},{final_results[key]}\n")
