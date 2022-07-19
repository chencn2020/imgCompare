nohup python3 -u main_flask.py > test.log 2>&1 &
echo $! > save_pid.txt