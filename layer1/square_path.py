import numpy as np


def square_path(width_of_square=30, height_of_square=30, start_tile=10, x_len_div = 50, y_len_div=50):
    '''
    create a list of tiles numbers
    x,y_len_div: number of tiles in each directions
    '''
    # First try => only up right down left moves is applied
    # tile_lst = list(range(x_len_div*y_len_div))
    # tiles_lst_col = np.array_split(tile_lst, x_len_div)
    # for index, value in enumerate(tiles_lst_col):
    #     if start_tile in value:
    #         col = index
    #
    # if start_tile in range(0, 2500):
    #     if start_tile + height_of_square < max(tiles_lst_col[col]):
    #         if start_tile + (width_of_square * x_len_div) < max(tiles_lst_col[-1]):
    #             up_range = list(range(start_tile, start_tile + height_of_square + 1, 1))
    #             right_top_pos = width_of_square * x_len_div + max(up_range)
    #             right_top_range = list(range(max(up_range) + x_len_div, right_top_pos + 1, x_len_div))
    #
    #             right_bot_pos = max(right_top_range) - height_of_square
    #             right_bot_range = list(range(right_top_pos - 1, right_bot_pos - 1, -1))
    #             left_bot_range = list(range(min(right_bot_range) - x_len_div, start_tile - 1, -x_len_div))
    #         else:
    #             return ValueError
    #     else:
    #         return ValueError
    # else:
    #     return ValueError
    # print(f' up_range is {up_range}')
    # print(f' right_top_range is {right_top_range}')
    # print(f' right_bot_range is {right_bot_range}')
    # print(f' left_bot_range is {left_bot_range}')
    tile_lst = list(range(x_len_div * y_len_div))
    tiles_lst_col = np.array_split(tile_lst, x_len_div)
    for index, value in enumerate(tiles_lst_col):
        if start_tile in value:
            col = index

    if start_tile in range(0, 2500):
        if start_tile % y_len_div + height_of_square < max(tiles_lst_col[col]):
            if start_tile % x_len_div + width_of_square < max(tiles_lst_col[-1]):
                up_range = list(range(start_tile, start_tile + height_of_square + 1, 1))
                right_top_pos = width_of_square * x_len_div + max(up_range)
                right_top_range = list(range(max(up_range) + x_len_div, right_top_pos + 1, x_len_div))

                right_bot_pos = max(right_top_range) - height_of_square
                right_bot_range = list(range(right_top_pos - 1, right_bot_pos - 1, -1))
                left_bot_range = list(range(min(right_bot_range) - x_len_div, start_tile - 1, -x_len_div))
            else:
                raise ValueError
        else:
            raise ValueError
    else:
        raise ValueError
    #print(f' up_range is {up_range}')
    #print(f' right_top_range is {right_top_range}')
    #print(f' right_bot_range is {right_bot_range}')
    #print(f' left_bot_range is {left_bot_range}')
    return up_range, right_top_range, right_bot_range, left_bot_range
