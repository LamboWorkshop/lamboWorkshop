#/bin/bash

# in crontab : */5 * * * * /home/segfault42/Documents/scalping_bot/script/update_prod.sh

cd /home/segfault42/Documents/scalping-bot
git log -1 --pretty=format:"%H" > ./latest
git pull origin master
git log -1 --pretty=format:"%H" > /tmp/pull
diff --brief <(sort /tmp/pull) <(sort ./latest) >/dev/null

comp_value=$?

if [ $comp_value -eq 1 ]
then
	/usr/local/bin/docker-compose down && /usr/local/bin/docker-compose -f docker-compose.prod.yml up -d --no-deps --build
fi
