# -*- coding: utf-8 -*-
# @Time    : 2022/3/29 17:28
# @Author  : Zevin
# @Email   : chencn2021@163.com
# @File    : checkUseInfo.py
# @Software: PyCharm

import sqlite3
import os

class checkUserInfo():
    def __init__(self):
        # print(os.getcwd())
        # print(os.path.join(os.getcwd(), 'imgCompareSystem',
        #                                                  'source/database/userInfo.db'))
        self.userDatabase = sqlite3.connect(os.path.join(os.getcwd(), 'source/database/userInfo.db'), check_same_thread=False)
        self.cu = self.userDatabase.cursor()

    def commit_sql(self):
        self.userDatabase.commit()

    def create_table(self, sql):
        self.cu.execute(sql)

    def insert_user(self, user_name: list, password: list):
        userInfo = zip(user_name, password)
        for userName, password in userInfo:
            self.cu.execute("insert into userInfo values (?,?)", (userName, password))
        self.commit_sql()

    def login_check(self, userName, password):
        sql = "select * from userInfo where userName = '{}' and password = '{}'".format(userName, password)
        self.cu.execute(sql)
        res = self.cu.fetchall()

        if len(res) == 0:
            return False
        else:
            return True

if __name__ == '__main__':
    sql = checkUserInfo()
    # sql.create_table("create table userInfo (userName varchar(10) primary key,password varchar(10))")

    # sql.insert_user(['czw', 'lb', 'wj', 'qhn', 'zxz', 'hlf', 'cmx', 'lr'],
    #                 ['czw', 'lb', 'wj', 'qhn', 'zxz', 'hlf', 'cmx', 'lr'])


    # print(sql.login_check("select * from userInfo where userName = 'czw' and password = '1'"))
    print(sql.login_check('czw', 'czw'))
    print(sql.login_check('czw', '1'))
    print(sql.login_check('czw', '1 or 1'))
    # print(sql.login_check("select * from userInfo where userName = 'czw'"))