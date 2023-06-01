import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib
# matplotlib.use('TkAgg')
from sig_plot import sig_plot
import numpy as np


def find_correlation(first_serie: list, second_serie: list, tile_postion_list=None, plotting=True, threed=True):
    if second_serie is not None:
        # rearrang_data based for each row
        new_serie1 = []
        new_serie2 = []
        index = 0
        for i in range(0, len(first_serie), 50):
            new_serie1.append(first_serie[i:i + 50])
            new_serie2.append(second_serie[i:i + 50])
            index += 1
        calculated_corr_coef_rows = np.corrcoef(new_serie1, new_serie2)
        calculated_corr_coef_1lst = np.corrcoef(first_serie, second_serie)
        # print(f"caulated coefficinet is: {calculated_corr_coef_rows}")
        # print(index, len(new_serie1))
        # fixme: Find corr for each row
        corr_row_by_row = []
        for i in range(len(new_serie1)):
            # print(len(new_serie1))
            corr_row_by_row.append(np.corrcoef(new_serie1[i], new_serie2[i]))
            # print(f"caulated coefficinet for row {i} is: {corr_row_by_row[i]}")
    else:
        calculated_corr_coef = np.corrcoef(new_serie1)
        print(calculated_corr_coef)
        calculated_corr_coef_1lst = np.corrcoef(first_serie, second_serie)

    # if plotting:
    #     # sig_plot(first_serie, second_serie, tile_position_list, threed)
    #     plt.figure(0)
    #     x_axis = range(len(first_serie))
    #     plt.scatter(x_axis, first_serie, marker="o", c='b')
    #     plt.scatter(x_axis, second_serie, marker='^', c='g')
    #     plt.xlabel("tiles number")
    #     plt.ylabel("BLER")
    #     plt.show()
    #
    # if threed:
    #     x_list = []
    #     y_list = []
    #     for i in tile_position_list:
    #         x = i[0]
    #         y = i[1]
    #         x_list.append(x)
    #         y_list.append(y)
    #     # print((y_list))
    #     values_list1 = first_serie
    #     plt.figure(1)
    #     plt.scatter(x_list, y_list, c= values_list1, cmap='Spectral')
    #     plt.xlabel("x (m)")
    #     plt.ylabel("y (m)")
    #     plt.colorbar()
    #     plt.title('BLER for factory with x50 y50, 5000 UEs to gNB x25 y55 p50 ')
    #     plt.show()
    #
    #     plt.figure(3)
    #     values_list2 = second_serie
    #     plt.scatter(x_list, y_list, c=values_list2, cmap='Spectral')
    #     plt.xlabel("x (m)")
    #     plt.ylabel("y (m)")
    #     plt.colorbar()
    #     plt.title('BLER for factory with x50 y50, 5000 UEs to gNB x25 y55 p50 ')
    #     plt.show()
    #
    #     plt.figure()
    #     ax = plt.axes(projection = "3d")
    #     tile = np.arange(0,50)
    #     X,Y = np.meshgrid(tile, tile)
    #     z = np.ones([50,50])
    #     value_reshape1 = values_list1.reshape((50, 50))
    #     value_reshape2=values_list2.reshape((50, 50))
    #     ax.plot_surface(X, Y, value_reshape1, alpha=0.3)
    #     ax.plot_surface(X, Y, value_reshape2, alpha = 0.5)
    #     plt.show()

        # fig = plt.figure()
        # ax = fig.add_subplot(111, projection='3d')
        # X, Z = np.meshgrid(x_list, y_list)
        # ax.plot_surface(X, Z, values_list1)

    return calculated_corr_coef_rows, calculated_corr_coef_1lst, corr_row_by_row
