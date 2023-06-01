import numpy as np
from numpy.core.fromnumeric import size

import seaborn as sns
# sns.set_theme()

import matplotlib.pylab as plt

import json

# uniform_data = np.random.rand(10, 12)
# ax = sns.heatmap(uniform_data, vmin=0, vmax=1)

sd = 20 # width/length subdivisions
bs_x = 50 # BS x position
bs_y = 50 # BS y position
payload_size = 10

data_file_name = f"bs_uc3_ls{sd}_ws{sd}_x{bs_x}_y{bs_y}_n3000_p{payload_size}.json"

with open(data_file_name) as f:
  data_dict:dict = json.load(f)

data_matrix_dict = {}

for coords, value in data_dict.items():
  # col, row = ( float(v) for v in coords.split(",") )
  col, row = coords.split(",")
  if row not in data_matrix_dict:
    data_matrix_dict[row] = { col: value }
  else:
    data_matrix_dict[row][col] = value

# print(f"{data_matrix_dict = }")

data_matrix_list = [
  [ float(data_matrix_dict[row][col]) for col in data_matrix_dict[row] ]
    for row in data_matrix_dict
]

# row_list = [ r for r in data_matrix_dict ]
# col_list = [ c for c in data_matrix_dict[row_list[0]] ]

# print(f"{data_matrix_list = }")

ax = sns.heatmap(data_matrix_list,
  cmap = sns.cm.rocket_r,
  cbar = False,
  xticklabels = False,
  yticklabels = False,
  linewidths = 0,
  square = True)

ax.invert_yaxis()

# ax.scatter(bs_x, bs_y, marker="o", s=10, c="k")

plt.savefig(data_file_name.replace(".json", "_heatmap.pdf"), bbox_inches='tight')