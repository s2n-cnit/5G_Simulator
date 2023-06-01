import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import plotly.graph_objects as go

matplotlib.use('TkAgg')


def tile_plot(values_list1, values_list2, first_gnodb, second_gnodb):
    plt.figure()
    fig = go.Figure()

    ax = plt.axes(projection="3d")
    tile = np.arange(0, 50)
    X, Y = np.meshgrid(tile, tile)
    z = np.ones([50, 50])
    value_reshape1 = values_list1.reshape((50, 50))
    value_reshape2 = values_list2.reshape((50, 50))
    surf1 = ax.plot_surface(X, Y, value_reshape1, alpha=0.3, label=f"gNodeB={first_gnodb}")
    surf2 = ax.plot_surface(X, Y, value_reshape2, alpha=0.5, label=f"gNodeB={second_gnodb}")
    # Adding legend surf1 , surf are required
    surf1._edgecolors2d = surf1._edgecolor3d
    surf1._facecolors2d = surf1._facecolor3d
    surf2._edgecolors2d = surf2._edgecolor3d
    surf2._facecolors2d = surf2._facecolor3d
    ax.set_xlabel("Tile")
    ax.set_ylabel("Tile")
    ax.set_zlabel("BLER")
    ax.legend()
    plt.show()
