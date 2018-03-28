#! /usr/bin/env python
# Author: Brendan Ryan
# Date created: 3/9/2018
# Watches a directory of Opto recipes and commits any changes to the GitHub repo

import os
import sys
import time
import datetime
import subprocess
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

def commit_changes():
    try:
        subprocess.check_call('git add *')
        subprocess.check_call('git commit -m "' + '{:%b %d, %Y, %I:%M %p }'.format(datetime.datetime.now()) + '"')
        subprocess.check_call('git push origin master')
    except:
        print "Unable to commit files to repository."

class MyEvent(PatternMatchingEventHandler):
    patterns = ["*.txt"]

    timer = time.time() - 3600

    def check_timer(self):
         return time.time() - self.timer > 3600

    def process(self, event):
        # only commit changes once per hour
        if self.check_timer():
            commit_changes()
            self.timer = time.time()

    def on_modified(self, event):
        self.process(event)

    def on_created(self, event):
        self.process(event)

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else '.'
    os.chdir(path)
    event_handler = MyEvent()
    observer = Observer()
    observer.schedule(event_handler, path)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()