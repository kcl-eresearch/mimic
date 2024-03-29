#!/usr/bin/python

import os
import datetime

def is_heartbeat_active(filename):
    mtime = os.path.getmtime(filename)
    now = datetime.datetime.now().timestamp()
    if now - mtime < 600:
        return True
    return False

def stop_app(username, app):
    if app == 'vscode':
        heartbeat = "/users/%s/.local/share/code-server/heartbeat" % username
        if os.path.exists(heartbeat) and is_heartbeat_active(heartbeat):
            return
        print("Stopping %s-%s" % (username, app))
        os.system("systemctl stop code-server@%s" % username)
        return

    raise Exception("Unsupported app: %s" % app)


# Search /var/run/mimic/{username}/{app}.sock
path = "/var/run/mimic"
for username in os.listdir(path):
    for app in os.listdir("%s/%s" % (path, username)):
        if app.endswith(".sock"):
            stop_app(username, app[:-5])
