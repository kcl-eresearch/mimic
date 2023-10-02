#
# Mimic - Deploy web applications as users
#

import time
import requests

class MimicClient:
    def __init__(self, ctx) -> None:
        self.ctx = ctx
    
    def run_thread(self) -> None:
        while True:
            self.heartbeat()
            time.sleep(30)
        
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
