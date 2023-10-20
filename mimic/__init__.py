#
# Mimic - Deploy web applications as users
#

__VERSION__ = "1.1"

from multiprocessing import Process
from mimic.common.context import MimicContext
from mimic.client.client import MimicClient
from mimic.client.web.flask import MimicClientFlask
from mimic.server.server import MimicServer
from mimic.server.web.flask import MimicServerFlask


def run_client(app):
    ctx = MimicContext({"config": "/etc/mimic/mimic-%s.conf" % app})

    # Send a message to the server
    client = MimicClient(ctx)
    client.register()
    client_thread = Process(target=client.run_thread)
    client_thread.start()
    ctx.logger.info("Spawning client thread.")

    # Web thread.
    webserver = MimicClientFlask(ctx)
    if ctx.config.getboolean("client", "debug", fallback=False):
        webserver.run()

        # Unregister.
        client.unregister()
    else:
        return webserver.app


def run_server():
    ctx = MimicContext()

    server = MimicServer(ctx)
    server_thread = Process(target=server.run_thread)
    server_thread.start()

    # Web thread.
    webserver = MimicServerFlask(ctx, server)
    if ctx.config.getboolean("client", "debug", fallback=False):
        webserver.run()
    else:
        return webserver.app
