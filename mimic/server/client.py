#
# Mimic - Deploy web applications as users
#

from multiprocessing import Process
from mimic.common.utils import close_thread

class MimicServerClient:
    def __init__(self, client_id, sck) -> None:
        self.client_id = client_id
        self.sck = sck
        self.running = True
        self.thread = Process(target=self.run)
        self.thread.start()
    
    def is_alive(self) -> bool:
        return self.thread.is_alive()
    
    def terminate(self) -> None:
        self.running = False
        self.thread.join(1)
        close_thread(self.thread)

    def run(self) -> None:
        while self.running:
            data = self.sck.recv(1024)
            if not data:
                break
            print ('Received', repr(data))
            if data == b'CLOSE':
                break

        print ("Closing connection to client %s" % self.client_id)
        self.sck.send('CLOSED'.encode())
        self.sck.close()
