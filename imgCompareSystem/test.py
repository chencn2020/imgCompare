# -*- coding: utf-8 -*-
# @Time    : 2022/3/30 11:19
# @Author  : Zevin
# @Email   : chencn2021@163.com
# @File    : test.py
# @Software: PyCharm

from utils import compareImgDatabase as CID

if __name__ == '__main__':
    test = CID.compareImgDatabase('test1')
    # test.show_all()

    # case = test.get_a_not_finish_case('czw')
    # print(case)
    # print(test.get_finish_info('czw'))

    # case = test.get_a_not_finish_case('czw')
    # print(123, case)
    # test.update_choice(case[0], 'czw', 0)
    # test.show_all()
    #
    # case = test.get_a_not_finish_case('czw')
    # test.update_choice(case, 'czw', 1)
    # test.show_all()
    #
    # case = test.get_a_not_finish_case('czw')
    # test.update_choice(case[0], 'czw', 1)
    # test.show_all()
    test.get_case_score_details()
    # print(case)
