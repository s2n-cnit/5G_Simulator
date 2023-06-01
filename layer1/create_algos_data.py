import numpy as np


def create_algos_data(ue_dir, correlated_gnodbs_id_set, all_bler_list, write_to_file=True,
                      file_name='ue_gnodb_set_highbler.txt', ue_tile_number=1):
    output = dict()
    output[ue_dir] = [(ue_tile_number, key, value, np.mean(all_bler_list[key])) for key, value in
                      correlated_gnodbs_id_set.items()]
    if write_to_file:
        with open(file_name, 'w') as f:
            f.write(str(output))

    return output
