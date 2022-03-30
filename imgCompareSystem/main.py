from flask import Flask
from flask import request
import json
from flask import Flask, render_template, request, Response
from utils import checkUseInfo

app = Flask(__name__)
checkUser = checkUseInfo.checkUserInfo()

@app.route('/', methods=['GET'])
def log_in(info=''):
    return render_template('index.html', info=info)


@app.route("/login_user", methods=['POST', 'GET'])  # 用户登录
def login_user():
    userName = request.form.get("userName")
    password = request.form.get("password")

    print(userName, password)

    res = checkUser.login_check(userName, password)

    print('用户{}登录{}'.format(userName, res))

    if res:
        return render_template('imgCompareSystemMainUI.html')
    else:
        return Response(log_in("alert('密码错误')"))

    # result = p.run_store_produce("EXEC log_in_customer '{}', '{}'".format(password, phone))
    # if len(result) != 0:
    #     global customer_id_
    #     global customer_name
    #     global customer_phone
    #     customer_phone = phone
    #     customer_id_ = str(result[0][0])
    #     customer_name = str(result[0][1])
    #     return Response(index())
    # else:
    #     return render_template("loginlqc.html")

# 设置访问URL：'/plus'，methods：允许哪种方式访问
@app.route('/plus', methods=['POST'])
def plus():
    data = json.loads(request.data.decode())
    x = data['x']
    y = data['y']

    return json.dumps(x + y)


if __name__ == '__main__':
    # 设置host，端口8080。threaded=True 代表开启多线程
    app.run(host='0.0.0.0', port=8080, threaded=True)
