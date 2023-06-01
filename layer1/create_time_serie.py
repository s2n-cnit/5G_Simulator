import matplotlib.pyplot as plt
import numpy as np
# following can be removed only to plot are used in pycharm
import matplotlib as mpl

mpl.use('TkAgg')  # !IMPORTANT

def repeat_lst_items_randomly(input_list: list, max_number_of_repeatation):
    '''
    Generate repated list, each item has repeated randomly
    Genearte repeated list each one is guassian random number with mean value of bler 
    '''
    repeated_list = []
    for item in input_list:
        random_number = np.random.randint(100, max_number_of_repeatation)
        for i in range(random_number):
            repeated_list.append(item)
    return repeated_list


def create_time_serie(gnodb_postion_lst: list, serie: list, max_number_of_repeatation: int = 100, plotting=False,
                      type_rand=None, ue_dir=[1,1]):
    '''
    param: serie : list of BLER list
    '''
    len_input = len(serie)
    # print(f'len gnodb_postion_lst is:{len(gnodb_postion_lst)} and for series is: {len(serie)}')
    # TODO: correct the code for odd number of inputs
    if len(gnodb_postion_lst) % 2 > 0:
        len_input -= 1

    if type_rand == 'Guassian':
        new_guass_serie_of_series = list()
        # print("###############################################")
        # print(f"DEBUC len serie is {len(serie)}")
        # for each_serie in serie:
        #     print(f"DEBUC len each_serie is {len(each_serie)}")
        #     ext_guass_lst = [np.random.normal(val, val / 10, max_number_of_repeatation) for val in each_serie]
        #     print(f"DEBUC len ext_guass_lst is {len(ext_guass_lst)}")
        #     new_guass_serie_of_series.append(ext_guass_lst)
        for each_serie in serie:
            ext_each_guass_lst = list()
            for val in each_serie:
                temp = list(np.random.normal(val, val / 50, max_number_of_repeatation))
                ext_each_guass_lst += temp
            new_guass_serie_of_series.append(ext_each_guass_lst)
        # print(f"DEBUG: len of new_guass_serie_of_series is : {len(new_guass_serie_of_series)}")
        repeated_serie = new_guass_serie_of_series ## Fixme: only for plotting !
    else:
        # Fixme: Adding random number of repetitions for each value
        repeated_serie = [np.repeat(item_lst, max_number_of_repeatation) for item_lst in serie]
        # print(f"DEBUG:ELSE len of repeated serie is : {len(repeated_serie)}")
    if plotting is True:
        if len_input < 9:
            fig, axs = plt.subplots(2, len_input // 2)
            fig.suptitle(f"BLER time series for UE {ue_dir}")
            # plt.subplots_adjust(top=0.90)
            for i in range(len_input):
                x_axis = range(len(repeated_serie[i]))
                # print(f'DEBUG: The len of serie {i} is {len(x_axis)}')
                if i < len_input // 2:
                    axs[0, i].plot(x_axis, repeated_serie[i])
                    # axs[0, i].set_title(f"gNodeB {gnodb_postion_lst[i]}")
                    axs[0, i].set_title(f"gNodeB {gnodb_postion_lst[i]}")
                    axs[0, i].set(xlabel=f"Each step = {max_number_of_repeatation} $\Delta t$", ylabel="BLER")
                    axs[0, i].set_ylim([0, 1])
                else:
                    j = i - len_input // 2
                    axs[1, j].plot(x_axis, repeated_serie[i])
                    axs[1, j].set_title(f"gNodeB {gnodb_postion_lst[i]}")
                    # axs[1, j].set(xlabel="Each step = rand(100,1000) $\Delta t$", ylabel="BLER")
                    axs[1, j].set(xlabel=f"Each step = {max_number_of_repeatation} $\Delta t$", ylabel="BLER")
                    axs[1, j].set_ylim([0, 1])
                    # print(repeated_serie[i])
            fig.tight_layout(h_pad=2)

        if len_input > 9:
            fig, axs = plt.subplots(4, len_input // 4)
            fig.tight_layout(h_pad=2)
            fig.suptitle(f"BLER Time series for ue={ue_dir}")
            plt.subplots_adjust(top=0.90)
            step_size = len_input // 4
            for i in range(len_input):
                x_axis = range(len(repeated_serie[i]))
                # print(f'DEBUG: len_input > 9: The len of serie {i} is {len(x_axis)}')
                if i < step_size:
                    axs[0, i].plot(x_axis, repeated_serie[i])
                    axs[0, i].set_title(f"gNodeB {gnodb_postion_lst[i]}")
                    axs[0, i].set(xlabel=f"Each step = {max_number_of_repeatation} $\Delta t$", ylabel="BLER")
                    axs[0, i].set_ylim([0, 1])
                elif step_size <= i < 2*step_size:
                    j = i - 2*step_size
                    axs[1, j].plot(x_axis, repeated_serie[i])
                    axs[1, j].set_title(f"gNodeB {gnodb_postion_lst[i]}")
                    # axs[1, j].set(xlabel="Each step = rand(100,1000) $\Delta t$", ylabel="BLER")
                    axs[1, j].set(xlabel=f"Each step = {max_number_of_repeatation} $\Delta t$", ylabel="BLER")
                    axs[1, j].set_ylim([0, 1])
                    # print(repeated_serie[i])
                elif 2*step_size <= i< 3*step_size:
                    j = i - 3*step_size
                    axs[2, j].plot(x_axis, repeated_serie[i])
                    axs[2, j].set_title(f"gNodeB {gnodb_postion_lst[i]}")
                    # axs[1, j].set(xlabel="Each step = rand(100,1000) $\Delta t$", ylabel="BLER")
                    axs[2, j].set(xlabel=f"Each step = {max_number_of_repeatation} $\Delta t$", ylabel="BLER")
                    axs[2, j].set_ylim([0, 1])
                    # print(repeated_serie[i])
                elif 3*step_size <= i < len_input:
                    j = i - len_input
                    axs[3, j].plot(x_axis, repeated_serie[i])
                    axs[3, j].set_title(f"gNodeB {gnodb_postion_lst[i]}")
                    # axs[1, j].set(xlabel="Each step = rand(100,1000) $\Delta t$", ylabel="BLER")
                    axs[3, j].set(xlabel=f"Each step = {max_number_of_repeatation} $\Delta t$", ylabel="BLER")
                    axs[3, j].set_ylim([0, 1])
                    # print(repeated_serie[i])
        plt.savefig(f'blers_time_serie_ue_{ue_dir}')
        plt.show()

    return list(repeated_serie)
