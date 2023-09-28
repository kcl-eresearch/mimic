#
# Mimic - Deploy web applications as users
#

from multiprocessing import Process
import time
from mimic.common.utils import close_thread
from mimic.common.context import MimicContext
from mimic.client.socket import MimicClientSocket
from mimic.server.socket import MimicServerSocket

def run_client():
    ctx = MimicContext()
    server = MimicClientSocket(ctx)
    socket_thread = Process(target=server.run)
    socket_thread.start()

    # TODO: main thread.
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    
    # Terminate server.
    server.terminate()
    close_thread(socket_thread)

def run_server():
    ctx = MimicContext()
    server = MimicServerSocket(ctx)
    socket_thread = Process(target=server.run)
    socket_thread.start()

    # Main thread ticker.
    try:
        while True:
            time.sleep(1)
            server.tidy_clients()
    except KeyboardInterrupt:
        pass
    
    # Terminate server.
    server.terminate()
    close_thread(socket_thread)
