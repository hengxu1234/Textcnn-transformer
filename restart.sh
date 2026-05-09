pid=$(ps aux | grep ad_detect | grep -v grep | awk '{print $2}')
if [ ! -n "$pid" ] ;then
	echo "The ad_detect service is shutdown!"
	./start.sh
	echo "The ad_detect service is restart!"
else
	echo "The ad_detect service is running!"
	pid=$(ps aux | grep ad_detect | grep -v grep | awk '{print $2}')
  kill -9 $pid
  chmod +x cleanlog.sh && /usr/bin/nohup /bin/sh /devin/ad_detect/cleanlog.sh &
  /usr/bin/supervisorctl -c ad_detect.conf stop all
  supervisord -c ad_detect.conf
  supervisorctl -c ad_detect.conf reload
  supervisorctl -c ad_detect.conf status
  supervisorctl -c ad_detect.conf start all
  supervisorctl -c ad_detect.conf status
  echo "The ad_detect service is restart!"
fi
