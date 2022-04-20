from flask import Flask
from flask import request
import json
from flask import Flask, render_template, request, Response, redirect
from utils import checkUseInfo
from utils import compareImgDatabase as CID
import random
import string

# compareImgDatabase = 'test1'
# compareImgDatabase = 'TinyISP_ResizeCrop61_TIQA_20k'
compareImgDatabase = 'TinyISP_Crop61_SSIMOnly_20k'
print('测试数据集：', compareImgDatabase)
app = Flask(__name__, static_folder='', static_url_path='')
checkUser = checkUseInfo.checkUserInfo()
compareDB = CID.compareImgDatabase(compareImgDatabase)
userCookie = {}
imgInfoCookie = {}
userChoiceCookie = {}


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
    if request.method == "GET":
        return render_template("index.html")
    elif request.method == "POST":
        userName = request.form.get("userName")
        password = request.form.get("password")

        res = checkUser.login_check(userName, password)
        print('用户{}登录{}'.format(userName, res))

        if res:
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
    global load_info

    user_token = request.cookies.get("token")
    userName = get_key_from_dict(userCookie, user_token)
    print(user_token, userCookie, choice)

    if userName:
        if userName not in userChoiceCookie:
            userChoiceCookie[userName] = 0
        if request.method == "GET":
            [nowCase, img1, img2, res] = compareDB.get_a_not_finish_case(userName)
            if nowCase is not None:
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
        return render_template("loopPIC.html", now_case=nowCase, img1=gt, img2=notGt,
                               choose_gt_num=gtNum, not_choose_gt_num=notGtNum, not_diff_gt_num = noDiffNum,
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

    user_token = request.cookies.get("token")
    userName = get_key_from_dict(userCookie, user_token)

    if userName:
        if request.method == "GET":
            [finish_num, full_num] = compareDB.get_finish_info(userName)
            [nowCase, img1, img2, res] = compareDB.get_a_not_finish_case(userName)

            if nowCase is not None:
                imgInfoCookie[userName + nowCase] = int(res)
                tempInfo = load_info
                load_info = None
            else:
                tempInfo = "所有case均已完成"
            return render_template("imgCompareSystemMainUI.html", user_name=userName, dataset_judge=compareImgDatabase,
                                   now_case=nowCase, finish_num=finish_num, full_num=full_num, img1=img1, img2=img2,
                                   info=tempInfo)
        elif request.method == "POST":
            img_chosen = request.values['img_chosen']
            case_name = request.form.get('message')
            if userName + case_name not in imgInfoCookie or imgInfoCookie[userName + case_name] is None:
                return redirect('/service')
            if int(img_chosen) == 2:
                isGt = 2
            else:
                isGt = int(imgInfoCookie[userName + case_name] == int(img_chosen))
            print("用户{}在{}选择{}，是否GT{}".format(userName, case_name, img_chosen, isGt))

            res = compareDB.update_choice(case_name, userName, isGt)
            imgInfoCookie[userName + case_name] = None
            if res:
                load_info = "提交完成，等待系统继续分配"
                return redirect('/service')
    print('用户登录过期')
    return render_template('index.html', info="登录过期，请重新登录")


@app.route('/analyze', methods=['POST', 'GET'])
def analyze():
    user_token = request.cookies.get("token")
    userName = get_key_from_dict(userCookie, user_token)

    if userName:
        res = compareDB.get_case_score_details()
        piInfo = compareDB.analyse_res()
        piRes = []
        for index, info in piInfo:
            piRes.append('{},{},{}'.format(info[0], info[1], info[2]))
        print('res', '!'.join(res))
        print('piRes', '!'.join(piRes))
        return render_template('analyze.html', order_num=len(res), order_list='!'.join(res), piNum=len(piRes),
                               piInfo='!'.join(piRes))
    print('用户登录过期')
    return render_template('index.html', info="登录过期，请重新登录")


if __name__ == '__main__':
    # 设置host，端口8080。threaded=True 代表开启多线程
    app.run(host='0.0.0.0', port=7568, threaded=True)
