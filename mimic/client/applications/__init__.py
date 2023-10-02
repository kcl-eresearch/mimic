#
# Mimic - Deploy web applications as users
#

import datetime
import os

class App:
    def __init__(self, ctx) -> None:
        self.ctx = ctx

    def run(self, username) -> None:
        raise NotImplementedError()

    def wait_for_startup(self) -> None:
        raise NotImplementedError()

    def check_heartbeat(self, username) -> bool:
        raise NotImplementedError()

    def is_heartbeat_active(self, filename):
        mtime = os.path.getmtime(filename)
        now = datetime.datetime.now().timestamp()
        if now - mtime < 600:
            return True
        return False
