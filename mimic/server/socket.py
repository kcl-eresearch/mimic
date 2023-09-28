#
# Mimic - Deploy web applications as users
#

import ssl
import socket

from mimic.server.client import MimicServerClient

class MimicServerSocket:
    def __init__(self, ctx) -> None:
        self.ctx = ctx
        self.active_clients = {}
    
    def terminate(self) -> None:
        self.running = False

    def accept_clients(self, socket) -> None:
        self.running = True
        try:
            while self.running:
                conn, addr = socket.accept()
                client_name = "%s:%s" % (addr[0], addr[1])
                print ('Got connection from', client_name )
                conn.send(b'WELCOME')
                client = MimicServerClient(client_name, conn)
                self.active_clients[client_name] = client
        except:
            pass

    def tidy_clients(self) -> None:
        self.active_clients = {k:v for k,v in self.active_clients.items() if v.is_alive()}

    def run(self) -> None:
        tls_enabled = self.ctx.config.getboolean('tls', 'enabled', fallback=False)
        host_ip = self.ctx.config.get('server', 'listen_ip', fallback='127.0.0.1')
        host_port = int(self.ctx.config.get('server', 'listen_port', fallback=9600))

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
            sock.bind((host_ip, host_port))
            sock.listen(5)

            if tls_enabled:
                certchain = self.ctx.config.get('tls', 'chain', fallback=None)
                privatekey = self.ctx.config.get('tls', 'private_key', fallback=None)
                context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                context.load_cert_chain(certchain, privatekey)
                with context.wrap_socket(sock, server_side=True) as ssock:
                    self.accept_clients(ssock)
            else:
                self.accept_clients(sock)

        for client in self.active_clients:
            client.terminate()
        self.active_clients = {}
