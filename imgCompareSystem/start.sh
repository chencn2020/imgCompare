nohup python3 -u main.py > test.log 2>&1 &
echo $! > save_pid.txt