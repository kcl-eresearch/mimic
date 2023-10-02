#
# Mimic - Deploy web applications as users
#

import time

class MimicServer:
    def __init__(self, ctx) -> None:
        self.ctx = ctx
        self.active_clients = {}
    
    def register_client(self, client) -> None:
        self.active_clients[client.name] = client
    
    def heartbeat_client(self, client_name) -> None:
        if client_name not in self.active_clients:
            return
        self.active_clients[client_name].heartbeat()
    
    def unregister_client(self, client_name) -> None:
        if client_name not in self.active_clients:
            return
        del self.active_clients[client_name]

    def tick(self) -> None:
        self.active_clients = {k:v for k,v in self.active_clients.items() if v.is_alive()}

    def run_thread(self) -> None:
        while True:
            self.tick()
            time.sleep(1)
