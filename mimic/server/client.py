#
# Mimic - Deploy web applications as users
#

import time

class MimicServerClient:
    def __init__(self, ctx, name, url) -> None:
        self._ctx = ctx

        # Client data.
        self.name = name
        self.url = url
        self.load = 0
        self.heartbeat()
    
    def heartbeat(self, client_load) -> None:
        self._last_heartbeat = time.time()
        self.load = client_load
    
    def is_alive(self) -> bool:
        return self._last_heartbeat > time.time() - 300
