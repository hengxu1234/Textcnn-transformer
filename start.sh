chmod +x cleanlog.sh && /usr/bin/nohup /bin/sh /devin/ad_detect/cleanlog.sh &

supervisord -c ad_detect.conf
supervisorctl -c ad_detect.conf start all
supervisorctl -c ad_detect.conf status
tail -f ./logs/gunicorn/gunicorn.log
