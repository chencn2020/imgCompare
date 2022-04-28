from flask import Flask
from flask import request
import json
from flask import Flask, render_template, request, Response, redirect
from utils import checkUseInfo
from utils import compareImgDatabase as CID
import random
import string
import threading

# compareImgDatabase = 'test1'
# compareImgDatabase = 'TinyISP_ResizeCrop61_TIQA_20k'
# compareImgDatabase = 'TinyISP_Crop61_SSIMOnly_20k'
# compareImgDatabase = 'TinyISP_Full61_TeacherIQA_SSIM_PSNR'
compareImgDatabase = 'test'
print('测试数据集：', compareImgDatabase)
app = Flask(__name__, static_folder='', static_url_path='')
checkUser = checkUseInfo.checkUserInfo()
compareDB = CID.compareImgDatabase(compareImgDatabase)
userCookie = {}
imgInfoCookie = {}
userChoiceCookie = {}
get_case_lock = threading.Lock()
get_case_submit_lock = threading.Lock()

userCase = {

}


def get_random_cookie():
    data = string.digits + string.ascii_letters
    cookie = ""
    for i in range(11):
        cookie += random.choice(data)
    return cookie


def get_key_from_dict(searchDict, searchValue):
    for key, value in searchDict.items():
        if value == searchValue:
            return key
    return False


@app.route('/', methods=['GET', 'POST'])
def log_in():
    global userCase
    if request.method == "GET":
        return render_template("index.html")
    elif request.method == "POST":
        userName = request.form.get("userName")
        password = request.form.get("password")

        res = checkUser.login_check(userName, password)
        print('用户{}登录{}'.format(userName, res))

        if res:
            userCase[userName] = [None for i in range(16)]
            red = redirect('/service')
            cookie_data = get_random_cookie()
            userCookie[userName] = cookie_data
            red.set_cookie("token", cookie_data)
            return red
        else:
            return render_template('index.html', info="密码错误")


load_info = None


@app.route('/loopPic/<choice>', methods=['POST', 'GET'])
def loopPic(choice):
    print('\n-------------loopPic------------')
    global load_info

    user_token = request.cookies.get("token")
    userName = get_key_from_dict(userCookie, user_token)
    print(userName, user_token, userCookie, choice)

    if userName:
        if userName not in userChoiceCookie:
            userChoiceCookie[userName] = 0
        if request.method == "GET":
            [nowCase, img1, img2, res] = compareDB.get_a_not_finish_case(userName)
            if nowCase is not None and userName != 'czw':
                load_info = "请完成全部Case后再查看"
                return redirect('/service')
        elif request.method == 'POST':
            if choice == 'next':
                userChoiceCookie[userName] += 1
            elif choice == 'pre':
                userChoiceCookie[userName] -= 1
            else:
                pass
        [gt, notGt, gtNum, notGtNum, noDiffNum, nowCase] = compareDB.get_a_case_and_res(userChoiceCookie[userName])

        # 超管专用
        if gtNum + notGtNum + noDiffNum == 0:
            gtNum = 0
            notGtNum = 0
            noDiffNum = 0.1
        return render_template("loopPIC.html", now_case=nowCase, img1=gt, img2=notGt,
                               choose_gt_num=gtNum, not_choose_gt_num=notGtNum, not_diff_gt_num=noDiffNum,
                               all_people_num=gtNum + notGtNum + noDiffNum,
                               choose_gt_per=str(round(gtNum / (gtNum + notGtNum + noDiffNum), 4) * 100) + '%',
                               not_choose_gt_per=str(round(notGtNum / (gtNum + notGtNum + noDiffNum), 4) * 100) + '%',
                               not_diff_gt_per=str(round(noDiffNum / (gtNum + notGtNum + noDiffNum), 4) * 100) + '%',

                               )

    print('用户登录过期')
    return render_template('index.html', info="登录过期，请重新登录")


@app.route('/service', methods=['POST', 'GET'])
def server():
    global load_info
    global get_case_lock

    user_token = request.cookies.get("token")
    userName = get_key_from_dict(userCookie, user_token)

    print(userName)

    if userName:
        if request.method == "GET":

            try:
                get_case_lock.acquire(True)
                global userCase
                [finish_num, full_num] = compareDB.get_finish_info(userName)
                get_img_info = compareDB.get_a_not_finish_case(userName, userCase)
                print('get a case', get_img_info[0])

                if get_img_info[0] is not None:
                    userCase[userName] = get_img_info
                    tempInfo = load_info
                    load_info = None
                else:
                    userCase[userName] = [None for i in range(16)]
                    tempInfo = "所有case均已完成"
                print('get a case', userCase)
            finally:
                get_case_lock.release()

            return render_template("imgCompareSystemMainUI.html", user_name=userName, dataset_judge=compareImgDatabase,
                                   now_case=userCase[userName][0], finish_num=finish_num, full_num=full_num,
                                   img_url_1=userCase[userName][1], img_url_2=userCase[userName][2], img_url_3=userCase[userName][3],
                                   img_url_4=userCase[userName][4], img_url_5=userCase[userName][5],
                                   img_url_6=userCase[userName][6], img_url_7=userCase[userName][7], img_url_8=userCase[userName][8],
                                   img_url_9=userCase[userName][9], img_url_10=userCase[userName][10],
                                   img_url_11=userCase[userName][11], img_url_12=userCase[userName][12],
                                   img_url_13=userCase[userName][13], img_url_14=userCase[userName][14],
                                   img_url_15=userCase[userName][15],
                                   info=tempInfo)
        elif request.method == "POST":
            try:
                get_case_submit_lock.acquire(True)
                res = eval(request.data)
                img_chosen = str(res['img_chosen'])
                case_name = str(res['message']).split(': ')[-1]

                print(img_chosen, case_name)
                if userName not in userCase or userCase[userName] is None:
                    return redirect('/service')
                print("用户{}在{}选择{}".format(userName, case_name, img_chosen))
                res = compareDB.update_choice(case_name, userName, img_chosen)
                userCase[userName] = [None for i in range(16)]
                if res:
                    load_info = "提交完成，等待系统继续分配"
            finally:
                get_case_submit_lock.release()
                # return redirect('/service')
    print('用户登录过期')
    return render_template('index.html', info="登录过期，请重新登录")


@app.route('/analyze', methods=['POST', 'GET'])
def analyze():
    user_token = request.cookies.get("token")
    userName = get_key_from_dict(userCookie, user_token)

    if userName:
        piInfo = compareDB.analyse_res()
        piRes = []
        for index, userName, res in piInfo:
            piRes.append('{},{},{}'.format(index, userName, str(res)))
        print('piRes', '!'.join(piRes))
        return render_template('analyze.html', order_num=len(piRes),
                               order_list='!'.join(piRes))
    print('用户登录过期')
    return render_template('index.html', info="登录过期，请重新登录")


if __name__ == '__main__':
    # 设置host，端口8080。threaded=True 代表开启多线程
    app.run(host='0.0.0.0', port=7568, threaded=True)
