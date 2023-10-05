#
# Mimic - Deploy web applications as users
#

import time

class MimicServer:
    def __init__(self, ctx) -> None:
        self.ctx = ctx
        self.active_clients = {}
    
    def register_client(self, client) -> None:
        self.ctx.logger.info("Registering client %s" % client.name)
        self.active_clients[client.name] = client
    
    def heartbeat_client(self, client_name, client_load) -> None:
        if client_name not in self.active_clients:
            return
        self.active_clients[client_name].heartbeat(client_load)
    
    def unregister_client(self, client_name) -> None:
        if client_name not in self.active_clients:
            return
        self.ctx.logger.info("Unregistering client %s" % client_name)
        del self.active_clients[client_name]

    def run_thread(self) -> None:
        while True:
            self.active_clients = {k:v for k,v in self.active_clients.items() if v.is_alive()}
            time.sleep(1)
