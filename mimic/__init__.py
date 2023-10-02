#
# Mimic - Deploy web applications as users
#

from multiprocessing import Process
from mimic.common.context import MimicContext
from mimic.client.client import MimicClient
from mimic.client.web.flask import MimicClientFlask
from mimic.server.server import MimicServer
from mimic.server.web.flask import MimicServerFlask

def run_client():
    ctx = MimicContext()

    # Send a message to the server
    client = MimicClient(ctx)
    client.register()
    client_thread = Process(target=client.run_thread)
    client_thread.start()

    # Web thread.
    webserver = MimicClientFlask(ctx)
    webserver.run()

    # Unregister.
    client.unregister()

def run_server():
    ctx = MimicContext()

    server = MimicServer(ctx)
    server_thread = Process(target=server.run_thread)
    server_thread.start()

    # Web thread.
    webserver = MimicServerFlask(ctx, server)
    webserver.run()
