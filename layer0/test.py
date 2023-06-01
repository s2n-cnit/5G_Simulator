# from compute_bler import compute_bler
# changed to add bler distr
from compute_bler_mean_bler import compute_bler

import json
from pathlib import Path

import multiprocessing

# Use Argparse to make an easy input
import argparse
parser = argparse.ArgumentParser(description="ue input for multiple ue path running")
parser.add_argument("ue_cor", nargs='*', help= " input ue position, usage: 1 1 0")
args = parser.parse_args()
print ("args.ue_cor", [int(i) for i in args.ue_cor])
def work(use_case, ls, ws, bs_x, bs_y, n_ue, payload):
    args = parser.parse_args()

    file_name = f"bs_uc{use_case}_ls{ls}_ws{ws}_x{bs_x}_y{bs_y}_n{n_ue}_p{payload}.json"
    cnit_file_name = f"bs_uc{use_case}_ls{ls}_ws{ws}_x{bs_x}_y{bs_y}_n{n_ue}_p{payload}_cnit.json"

    print(f"{file_name = }")

    if not Path(file_name).is_file():

        bler_dict, cnit_results_list = compute_bler(use_case_number=use_case, factory_length_subdivision=ls, factory_width_subdivision=ws,
            g_node_b_x=bs_x, g_node_b_y=bs_y, n_ues=n_ue, payload=payload,
                                                    ue_coordinates_x_y_z_argparse=[int(i) for i in args.ue_cor])
        # print(bler_dict)

        with open(file_name, "w") as f:
            # json.dump(
            #     { f"{k[0]:.3f},{k[1]:.3f}" : f"{v:.3e}" for k,v in bler_dict.items() },
            #     f
            # )
            # fixme: Alireza: Modified to accept NONE value for bler
            json.dump(
                { f"{k[0]:.3f},{k[1]:.3f}" : f"{v}" for k,v in bler_dict.items() },
                f
            )
        with open(cnit_file_name, "w") as f:
            # json.dump(
            #     { f"{k[0]:.3f},{k[1]:.3f}" : f"{v:.3e}" for k,v in bler_dict.items() },
            #     f
            # )
            # fixme: Alireza: Modified to accept NONE value for bler
            json.dump(cnit_results_list,f)

        return True

    else:
        print(f"Skipping {file_name = }")
        return False

uc = 12 #3
# ls = 50
# ws = 50
# x = 50
# y = 50
n = 1 #5000 #10006
# p = 30

# for ls, ws in [ (20, 20) ]:
#     for p in [ 125, 150 ]:
#         for x in [ 25, 50, 75 ]:
#             for y in [ 25, 50, 75 ]:

#                 file_name = f"bs_uc{uc}_ls{ls}_ws{ws}_x{x}_y{y}_n{n}_p{p}.json"

#                 print(f"{file_name = }")

#                 if not Path(file_name).is_file():

#                     bler_dict = compute_bler(use_case_number=uc, factory_length_subdivision=ls, factory_width_subdivision=ws,
#                         g_node_b_x=x, g_node_b_y=y, n_ues=n, payload=p)
#                     # print(bler_dict)

#                     with open(file_name, "w") as f:
#                         json.dump(
#                             { f"{k[0]:.3f},{k[1]:.3f}" : f"{v:.3e}" for k,v in bler_dict.items() },
#                             f
#                         )
#                 else:
#                     print(f"Skipping {file_name = }")

parameter_list = []

for ls, ws in [ (50, 50) ]:
    # for p in [ 50, 75, 100, 125 ]:
    for p in [50]:
        # for x in [ 25, 50, 75 ]:
        #     for y in [ 25, 50, 75 ]:
        for x in [1, 25, 50, 75, 100]: # gNodBs x,y
            for y in [1, 25, 50, 75, 100]:
                parameter_list.append( (uc, ls, ws, x, y, n, p) )

n_cpu = multiprocessing.cpu_count() - 2

pool = multiprocessing.Pool(n_cpu)
pool_return_values = pool.starmap(work, [ (uc, ls, ws, x, y, n, p) for (uc, ls, ws, x, y, n, p) in parameter_list ])
