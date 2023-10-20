#
# Mimic - Deploy web applications as users
#

import time


class MimicServer:
    def __init__(self, ctx) -> None:
        self.ctx = ctx
        self.active_clients = {}

    def register_client(self, client) -> bool:
        if client.name in self.active_clients:
            self.ctx.logger.warning(
                "Client %s already registered, unregistering..." % client.name
            )
            self.unregister_client(client.name)
        self.ctx.logger.info("Registering client %s" % client.name)
        self.active_clients[client.name] = client
        return True

    def heartbeat_client(self, client_name, client_load) -> bool:
        if client_name not in self.active_clients:
            self.ctx.logger.warning("Client %s not registered" % client_name)
            return False
        self.active_clients[client_name].heartbeat(client_load)
        return True

    def unregister_client(self, client_name) -> bool:
        if client_name not in self.active_clients:
            self.ctx.logger.warning("Client %s not registered" % client_name)
            return False
        self.ctx.logger.info("Unregistering client %s" % client_name)
        del self.active_clients[client_name]
        return True

    def run_thread(self) -> None:
        while True:
            self.active_clients = {
                k: v for k, v in self.active_clients.items() if v.is_alive()
            }
            time.sleep(1)
