#
# Mimic - Deploy web applications as users
#

import time
import os
import requests

from mimic.client.applications.vscode import AppVSCode

class MimicClient:
    def __init__(self, ctx) -> None:
        self.ctx = ctx
    
    def get_app_object(self, app_name) -> None:
        if app_name == 'vscode':
            return AppVSCode(self.ctx)
        return None
    
    def spawn(self, username) -> None:
        app_name = self.ctx.config.get('client', 'app')

        app = self.get_app_object(app_name)
        if app is None:
            raise Exception("Unknown app: %s" % app_name)
    
        app.run(username)
        app.wait_for_startup()
    
    def run_thread(self) -> None:
        cull_time = time.time()
        while True:
            current_time = time.time()
            end_time = current_time + 30

            # Start off with a heartbeat.
            self.heartbeat()

            # Every 60 minutes, cull old sessions.
            if current_time - cull_time > 3600:
                cull_time = current_time

                # Cull old sessions.
                # Search /var/run/mimic/{username}/{app}.sock
                path = "/var/run/mimic"
                for username in os.listdir(path):
                    for socket in os.listdir("%s/%s" % (path, username)):
                        if socket.endswith(".sock"):
                            app = self.get_app_object(socket[:-5])
                            if app is None:
                                continue
                            app.check_heartbeat(username)

            ticktime = end_time - time.time()
            if ticktime > 0:
                time.sleep()
        
    def heartbeat(self) -> None:
        server_url = self.ctx.config.get('server', 'url')
        req = requests.post("%s/api/client/heartbeat" % server_url, data={
            'name': self.ctx.config.get('client', 'name'),
            'token': self.ctx.config.get('server', 'psk'),
        })
        if req.status_code != 200:
            self.ctx.logger.error("Failed to heartbeat client: %s" % req.text)

    def register(self) -> None:
        server_url = self.ctx.config.get('server', 'url')
        req = requests.post("%s/api/client/register" % server_url, data={
            'name': self.ctx.config.get('client', 'name'),
            'url': self.ctx.config.get('client', 'url'),
            'token': self.ctx.config.get('server', 'psk'),
        })
        if req.status_code != 200:
            raise Exception("Failed to register client: %s" % req.text)
    
    def unregister(self) -> None:
        server_url = self.ctx.config.get('server', 'url')
        req = requests.post("%s/api/client/unregister" % server_url, data={
            'name': self.ctx.config.get('client', 'name'),
            'token': self.ctx.config.get('server', 'psk'),
        })
        if req.status_code != 200:
            raise Exception("Failed to unregister client: %s" % req.text)
