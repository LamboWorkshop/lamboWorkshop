#!/usr/bin/python3

databaseToDump='lambo_trunk'
localDirectoryBackup='/tmp/psqlBackup'
containerDirectoryBackup='/var/lib/postgresql/data/backup/'

import os
import glob
import hashlib
from datetime import datetime
from pathlib import Path
import subprocess

now = datetime.now()
date=now.strftime("%d-%m-%Y")
time=now.strftime("%H:%M:%S")
dt_string=date+"-"+time

backupName=dt_string+"_lamboTrunk.sql"

Path(localDirectoryBackup).mkdir(parents=True, exist_ok=True)
out = subprocess.check_output('docker exec -i database /bin/bash -c "pg_dump -U postgres '+databaseToDump+' > '+'/tmp/'+backupName+'"', shell=True)
subprocess.check_output('docker cp database:/tmp/'+backupName+' '+localDirectoryBackup+'/'+backupName, shell=True)

backupList = glob.glob(localDirectoryBackup+"/*.sql")

print('Files list:', backupList)

if len(backupList) == 1:
    print('One file found. Send it to ObjectStorage')
    subprocess.check_output("s3cmd put "+localDirectoryBackup+"/"+backupName+" s3://lambo-bot/database-backup/"+date+"/"+backupName, shell=True)
elif len(backupList) == 2:
    print('Two file found. Send it to ObjectStorage if file differ')
    digests = {}
    for filename in backupList:
        hasher = hashlib.md5()
        with open(filename, 'rb') as f:
            buf = f.read()
            hasher.update(buf)
            a = hasher.hexdigest()
            digests[filename]=a
    if list(digests.values())[0] == list(digests.values())[1]:
        print('Files are same, remove duplicate')
        os.remove(localDirectoryBackup+'/'+backupName)
    else:
        print('Files differ, send the newest to ObjectStorage.')
        subprocess.check_output("s3cmd put "+localDirectoryBackup+"/"+backupName+" s3://lambo-bot/database-backup/"+date+"/"+backupName, shell=True)
        latest_file = min(backupList, key=os.path.getctime)
        print('Remove the old backup from local storage: ', latest_file)
        os.remove(latest_file)