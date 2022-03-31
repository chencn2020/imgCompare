# -*- coding: utf-8 -*-
# @Time    : 2022/3/30 11:07
# @Author  : Zevin
# @Email   : chencn2021@163.com
# @File    : compareImgDatabase.py
# @Software: PyCharm
import sqlite3
import os
import random

class compareImgDatabase:
    def __init__(self, testDatabaseName):
        self.casePath = os.path.join(os.getcwd(), 'source/ImgTest/{}'.format(testDatabaseName))
        self.sourcePath = os.path.join('./source/ImgTest/{}'.format(testDatabaseName))
        self.userDatabase = sqlite3.connect(
            os.path.join(os.getcwd(), 'source/ImgTest/{}/compareImgInfo.db'.format(testDatabaseName)),
            check_same_thread=False)
        self.cu = self.userDatabase.cursor()

        try:
            self.create_table()
        except:
            pass

    def get_all_case_name(self):
        caseName = []
        for case in os.listdir(self.casePath):
            if case.startswith('Case'):
                caseName.append(case)
        return caseName

    def commit_sql(self):
        self.userDatabase.commit()

    def create_table(self):
        sql = "create table compareImgInfo (caseName varchar(10), userName varchar(10), isGt bit, primary key(caseName,userName))"
        self.cu.execute(sql)

    def update_choice(self, case, user, isGt):
        sql = "INSERT INTO compareImgInfo (caseName, userName, isGt) VALUES ('{}', '{}', {})".format(case, user, int(isGt))
        try:
            self.cu.execute(sql)
            self.commit_sql()
            return True
        except Exception as e:
            print(e)
            return False

    def show_all(self):
        sql = "select * from compareImgInfo"
        self.cu.execute(sql)
        res = self.cu.fetchall()
        print('show_all', res)

    def analyse_res(self):
        sql = "select caseName, sum(isGt), count(userName) - sum(isGt) from compareImgInfo group by caseName"
        self.cu.execute(sql)
        res = self.cu.fetchall()
        print('analyse_res', res)
        return res

    def get_case_score_details(self):
        caseList = self.get_all_case_name()
        detailInfo = ['否', '是']
        analyse_res = []
        analyse_all = {}
        for case in caseList:
            sql = "select * from compareImgInfo where caseName = '{}'".format(case)
            self.cu.execute(sql)
            res = self.cu.fetchall()
            if len(res) > 0:
                if case not in analyse_all:
                    analyse_all[case] = [0, 0]
                for _, user, isGt in res:
                    analyse_res.append('{},{},{}'.format(case, user, detailInfo[isGt]))
                    analyse_all[case][isGt] += 1

        for key, value in analyse_all.items():
            analyse_res.append(','.join([key, '未选GT:{}'.format(value[0]), '选择GT:{}'.format(value[1])]))
        print('analyse_res', analyse_res)

        return analyse_res

    def get_finish_info(self, userName):
        allCase = self.get_all_case_name()
        allNum = len(allCase)

        sql = "select caseName from compareImgInfo where userName = '{}'".format(userName)
        self.cu.execute(sql)
        res = self.cu.fetchall()
        finishNum = len(res)

        return [finishNum, allNum]

    def get_a_not_finish_case(self, userName):
        allCase = self.get_all_case_name()
        sql = "select caseName from compareImgInfo where userName = '{}'".format(userName)
        self.cu.execute(sql)
        res = self.cu.fetchall()
        for index in range(len(res)):
            res[index] = res[index][0]

        print('get_a_not_finish_case', res)
        print('get_a_not_finish_case', allCase)

        for case in allCase:
            if case not in res:
                for file in os.listdir(os.path.join(self.casePath, case)):
                    if 'GT' in file:
                        gt = os.path.join(self.sourcePath, case, file)
                    else:
                        other = os.path.join(self.sourcePath, case, file)
                if random.random() < 0.5:
                    return [case, gt, other, 0]
                else:
                    return [case, other, gt, 1]
        return [None, None, None, None]

    def get_a_case_and_res(self, caseIndex):
        allCase = self.get_all_case_name()
        caseIndex = caseIndex % len(allCase)
        case = allCase[caseIndex]

        print('get_a_not_finish_case', allCase)

        for file in os.listdir(os.path.join(self.casePath, case)):
            if 'GT' in file:
                gt = os.path.join('.'+self.sourcePath, case, file)
            else:
                other = os.path.join('.'+self.sourcePath, case, file)

        sql = "select sum(isGt), count(userName) - sum(isGt) from compareImgInfo where caseName = '{}'".format(case)
        self.cu.execute(sql)
        res = self.cu.fetchall()
        print('analyse_res', res)
        print(gt, other)
        return [gt, other, res[0][0], res[0][1], case]


if __name__ == '__main__':
    test = compareImgDatabase('test1')
    test.show_all()
    test.update_choice('Case1', 'czw', 'gt')
    test.show_all()
    test.get_a_not_finish_case('czw')
