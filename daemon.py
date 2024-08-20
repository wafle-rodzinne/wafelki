import os

from flask_apscheduler import APScheduler
import datetime
'''
#function executed by scheduled job
def my_job(text):
    print(text, str(datetime.datetime.now()))

# Get the list of all files and directories
path = "./instance"
dir_list = os.listdir(path)
print("Files and directories in '", path, "' :")
# prints all files
print(dir_list)


scheduler = APScheduler()
scheduler.add_job(func=my_job, args=['job run'], trigger='interval', id='job', seconds=5)
scheduler.start()
'''

from time import sleep

while(True):
    print('job run', str(datetime.datetime.now()))
    sleep(5)
