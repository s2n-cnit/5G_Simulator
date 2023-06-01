# import matplotlib
import matplotlib.pyplot as plt
import plotly.graph_objects as go


# from tile_plot import tile_plot


# matplotlib.use('TkAgg')


def sig_plot(first_serie=None, first_gnodb="Not defined", second_gnodb="Not defined", second_serie=None,
             tile_postion_list=None, threed=None, tile_plt=False, path_plot=False, sq_tiles_lst=None, title_=None):
    # plt.close('all')
    fig = None
    fig_path_plot = None
    # if tile_postion_list is not None:
    #     if first_serie is not None:
    #         plt.figure()
    #         fig = go.Figure()
    #         x_axis = list(range(len(first_serie)))
    #         # print(x_axis)
    #         fig.add_trace(go.Scatter(x= x_axis, y =first_serie, name= f'gNodB={first_gnodb}', mode="markers",
    #                                  marker_symbol="circle"))
    #         # plt.scatter(x_axis, first_serie, marker="o", c='b', label=f'gNodB={first_gnodb}')
    #         if second_serie is not None:
    #             x_axis2 = lis(range(len(second_serie)))
    #             fig.add_trace(go.Scatter(x=x_axis2, y=second_serie, name=f'gNodB={second_gnodb}', mode="markers",
    #                                      marker_symbol="square"))
    #             # plt.scatter(x_axis2, second_serie, marker='^', c='g', label=f'gNodB={second_gnodb}')
    #         fig.update_layout(xaxis_title="tiles number", yaxis_title="BLER" )
    #         # fig.update_xaxes()
    #
    #         # plt.xlabel(f"tiles number")
    #         # plt.ylabel("BLER")
    #         # plt.legend()
    #         # plt.show()
    #         # return fig
    # if threed is not None:
    #     # Fixme: apply pyplot
    #     x_list = []
    #     y_list = []
    #     for i in tile_postion_list:
    #         x = i[0]
    #         y = i[1]
    #         x_list.append(x)
    #         y_list.append(y)
    #     # print((y_list))
    #     values_list1 = first_serie
    #     plt.figure()
    #     plt.scatter(x_list, y_list, c=values_list1, cmap='Spectral')
    #     plt.xlabel("x (m)")
    #     plt.ylabel("y (m)")
    #     plt.colorbar()
    #     plt.title(f'BLER for factory with x=100m y=100m z=10m, 1 UEs to gNB={first_gnodb} ')
    #     plt.show()
    #
    #     plt.figure()
    #     values_list2 = second_serie
    #     plt.scatter(x_list, y_list, c=values_list2, cmap='Spectral')
    #     plt.xlabel("x (m)")
    #     plt.ylabel("y (m)")
    #     plt.colorbar()
    #     plt.title(f'BLER for factory with x=100m y=100m z=10m, 1 UEs to gNB={second_gnodb} ')
    #     plt.show()
    #
    #     if tile_plt:
    #         tile_plot(values_list1, values_list2, first_gnodb, second_gnodb)

    if path_plot:
        if sq_tiles_lst is not None:
            x_lst = [i[0] for i in tile_postion_list]
            y_lst = [i[1] for i in tile_postion_list]
            sq_x_tils = [tile_postion_list[i][0] for i in sq_tiles_lst]
            sq_y_tils = [tile_postion_list[i][1] for i in sq_tiles_lst]
            # fig_path_plot = go.Figure()
            # fig_path_plot.add_trace(go.Scatter(x=x_lst, y=y_lst, mode="markers", name="factory tiles",
            #                                    marker_symbol="square", marker=dict(color="blue", size=8,
            #                                                                        line=dict(width=1))))
            # fig_path_plot.add_trace(go.Scatter(x=sq_x_tils, y=sq_y_tils, mode="markers", name="Machine movement",
            #                                    marker_symbol="square", marker=dict(color="red", size=8,
            #                                                                        line=dict(width=1))))

            # fig_path_plot.update_layout(xaxis_title="x tiles = factory width/50",
            #                             yaxis_title="y tiles = factory length/50",
            #                             title=dict(text=f"<b>{title_}</b>", y=0.95, x=0.5, xanchor='center',
            #                                        yanchor='top'))

            # ================= matplotlib show
            plt.figure()
            plt.scatter(x_lst, y_lst, label="Factory tiles")
            plt.scatter(sq_x_tils, sq_y_tils, label='Machine path')
            plt.title("Factory [100, 100, 10]")
            plt.xlabel("x tiles = factory width/50", fontsize=13)
            plt.ylabel("y tiles = factory width/50", fontsize=13)
            plt.legend(fontsize = 13)
            plt.show()
            # return fig_path_plot
        # fig = plt.figure()
        # ax = fig.add_subplot(111, projection='3d')
        # X, Z = np.meshgrid(x_list, y_list)
        # ax.plot_surface(X, Z, values_list1)


        # fig_path_plot.show()


    return {"fig": fig, "fig_path_plot": fig_path_plot}
