# -*- coding: utf-8 -*-
# @Time    : 2022/3/30 11:07
# @Author  : Zevin
# @Email   : chencn2021@163.com
# @File    : compareImgDatabase.py
# @Software: PyCharm
import sqlite3
import os
import random
import threading


class compareImgDatabase:
    def __init__(self, testDatabaseName):
        self.casePath = os.path.join(os.getcwd(), 'source/ImgTest/{}'.format(testDatabaseName))
        self.sourcePath = os.path.join('./source/ImgTest/{}'.format(testDatabaseName))
        self.userDatabase = sqlite3.connect(
            os.path.join(os.getcwd(), 'source/ImgTest/{}/chooseImgInfo.db'.format(testDatabaseName)),
            check_same_thread=False)
        self.cu = self.userDatabase.cursor()

        self.get_finish_lock = threading.Lock()
        self.get_a_not_finish_case_lock = threading.Lock()
        self.update_choice_lock = threading.Lock()

        try:
            self.create_table()
        except:
            pass

    def get_all_case_name(self):
        caseName = []
        for dataName in sorted(os.listdir(self.casePath)):
            if os.path.isdir(os.path.join(self.casePath, dataName)):
                for case in os.listdir(os.path.join(self.casePath, dataName)):
                    caseName.append('{}.{}'.format(dataName, case))
        return caseName

    def commit_sql(self):
        self.userDatabase.commit()

    def create_table(self):
        # img1 czw 1,2,4
        sql = "create table chooseImgInfo (caseName varchar(20), userName varchar(10), " \
              "chosenImg varchar(50), primary key(caseName,userName))"
        self.cu.execute(sql)

    def update_choice(self, case, user, chosenImg):
        sql = "INSERT INTO chooseImgInfo (caseName, userName, chosenImg) VALUES ('{}', '{}', '{}')".format(case, user,
                                                                                                         str(chosenImg))

        print(sql)
        try:
            self.update_choice_lock.acquire(True)
            self.cu.execute(sql)
            self.commit_sql()
            return True
        finally:
            self.update_choice_lock.release()
        return False

    def show_all(self):
        try:
            self.get_finish_lock.acquire(True)
            sql = "select * from chooseImgInfo"
            self.cu.execute(sql)
            res = self.cu.fetchall()
            print('show_all', res)
        finally:
            self.get_finish_lock.release()

    def analyse_res(self):
        try:
            self.get_finish_lock.acquire(True)
            sql = "select caseName, userName, chosenImg from chooseImgInfo"
            self.cu.execute(sql)
            res = self.cu.fetchall()
        finally:
            self.get_finish_lock.release()

        finalRes = []
        for case, user, choice in res:
            finalRes.append([case, user, choice])

        # finalRes.sort()
        # so = analyse_res.items()
        # so.sort(key = lambda x:x[0],reverse = False)

        print('analyse_res', finalRes)

        return finalRes

    def get_case_score_details(self):
        caseList = self.get_all_case_name()
        detailInfo = ['否', '是', '差不多']
        analyse_res = []
        analyse_all = {}
        try:
            self.get_finish_lock.acquire(True)
            for case in caseList:
                sql = "select * from chooseImgInfo where caseName = '{}'".format(case)
                self.cu.execute(sql)
                res = self.cu.fetchall()
                if len(res) > 0:
                    if case not in analyse_all:
                        analyse_all[case] = [0, 0, 0]
                    for _, user, isGt in res:
                        analyse_res.append('{},{},{},0'.format(case, user, detailInfo[isGt]))
                        analyse_all[case][isGt] += 1
        finally:
            self.get_finish_lock.release()
        for key, value in analyse_all.items():
            analyse_res.append(
                ','.join([key, '未选GT:{}'.format(value[0]), '选择GT:{}'.format(value[1]), '差不多:{}'.format(value[2])]))
        print('analyse_res', analyse_res)

        return analyse_res

    def get_finish_info(self, userName):
        allCase = self.get_all_case_name()
        allNum = len(allCase)
        try:
            self.get_finish_lock.acquire(True)
            # sql = "select caseName from chooseImgInfo where userName = '{}'".format(userName)
            sql = "select caseName from chooseImgInfo"
            self.cu.execute(sql)
            res = self.cu.fetchall()
            finishNum = len(res)
        finally:
            self.get_finish_lock.release()

        return [finishNum, allNum]

    def get_a_not_finish_case(self, userName, userCase: dict):
        allCase = self.get_all_case_name()
        try:
            self.get_a_not_finish_case_lock.acquire(True)
            # sql = "select caseName from chooseImgInfo where userName = '{}'".format(userName)
            sql = "select caseName from chooseImgInfo"
            self.cu.execute(sql)
            res = self.cu.fetchall()
            for index in range(len(res)):
                res[index] = res[index][0]

            print('get_a_not_finish_case', res)
            print('get_a_not_finish_case', allCase)
            print('get_a_not_finish_case', userCase)
        finally:
            self.get_a_not_finish_case_lock.release()

        for case in allCase:
            if case not in res and case not in userCase.values():
                casePath = case.split('.')
                casePath = os.path.join(self.sourcePath, casePath[0], casePath[1])

                return_res = [case]

                for i in range(1, 16):
                    return_res.append(os.path.join(casePath, '{}.jpg'.format(i)))
                return return_res

        return [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]

    def get_a_case_and_res(self, caseIndex):
        allCase = self.get_all_case_name()
        caseIndex = caseIndex % len(allCase)
        case = allCase[caseIndex]

        print('get_a_not_finish_case', allCase)

        for file in os.listdir(os.path.join(self.casePath, case)):
            if 'GT' in file:
                gt = os.path.join('.' + self.sourcePath, case, file)
            else:
                other = os.path.join('.' + self.sourcePath, case, file)

        sql = "select isGt from chooseImgInfo where caseName = '{}'".format(case)

        self.cu.execute(sql)
        res = self.cu.fetchall()
        print('analyse_res', res)

        resNum = [0, 0, 0]

        for choice in res:
            resNum[choice[0]] += 1
        print(gt, other)
        return [gt, other, resNum[1], resNum[0], resNum[2], case]


if __name__ == '__main__':
    test = compareImgDatabase('test1')
    test.show_all()
    test.update_choice('Case1', 'czw', 'gt')
    test.show_all()
    test.get_a_not_finish_case('czw')
