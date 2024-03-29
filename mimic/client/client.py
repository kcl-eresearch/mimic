#
# Mimic - Deploy web applications as users
#

import requests
import subprocess
import time
from mimic import __VERSION__ as MIMIC_VERSION


class MimicClient:
    def __init__(self, ctx) -> None:
        self.ctx = ctx
        self.load = 0

    def spawn(self, username) -> bool:
        app_name = self.ctx.config.get("client", "app")

        try:
            subprocess.check_output(
                ["sudo", "/usr/local/bin/mimic", app_name, username]
            )
            self.load += 1
            return True
        except Exception as e:
            pass

        return False

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
                try:
                    ret = subprocess.check_output(
                        ["sudo", "/usr/local/bin/mimic-cleanup"]
                    )
                    self.load -= int(ret)
                except Exception as e:
                    pass

            ticktime = end_time - time.time()
            if ticktime > 0:
                time.sleep(ticktime)

    def is_standalone(self) -> bool:
        return self.ctx.config.getboolean("client", "standalone", fallback=False)

    def heartbeat(self) -> None:
        if self.is_standalone():
            return

        # Send heartbeat.
        server_url = self.ctx.config.get("server", "url")
        req = requests.post(
            "%s/api/client/heartbeat" % server_url,
            data={
                "token": self.ctx.config.get("server", "psk"),
                "name": self.ctx.config.get("client", "name"),
                "load": self.load,
            },
        )
        if req.status_code != 200:
            self.ctx.logger.error("Failed to heartbeat client, trying to re-register. Got '%s'" % req.text)
            self.register()

    def register(self) -> None:
        if self.is_standalone():
            return

        server_url = self.ctx.config.get("server", "url")
        req = requests.post(
            "%s/api/client/register" % server_url,
            data={
                "token": self.ctx.config.get("server", "psk"),
                "name": self.ctx.config.get("client", "name"),
                "url": self.ctx.config.get("client", "url"),
                "version": MIMIC_VERSION,
            },
        )
        if req.status_code != 200:
            raise Exception("Failed to register client: %s" % req.text)

    def unregister(self) -> None:
        if self.is_standalone():
            return

        server_url = self.ctx.config.get("server", "url")
        req = requests.post(
            "%s/api/client/unregister" % server_url,
            data={
                "token": self.ctx.config.get("server", "psk"),
                "name": self.ctx.config.get("client", "name"),
            },
        )
        if req.status_code != 200:
            raise Exception("Failed to unregister client: %s" % req.text)
