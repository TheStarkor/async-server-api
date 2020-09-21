redis-server --daemonize yes
conda activate flask
pm2 start run_model_server.py --interpreter ~/anaconda3/envs/flask/bin/python
pm2 start run_web_server.py --interpreter ~/anaconda3/envs/flask/bin/python