#
# Mimic - Deploy web applications as users
#

import dns.resolver
import sys
import ssl
import socket

class MimicClientSocket:
    def __init__(self, ctx) -> None:
        self.ctx = ctx
    
    def terminate(self) -> None:
        self.running = False
    
    def run_client_thread(self, socket) -> None:
        self.running = True
        while self.running:
            data = socket.recv(1024)
            if not data:
                break
            print ('Received', repr(data))
            if data == b'CLOSED':
                break
        socket.close()
        self.running = False

    def run(self) -> None:
        tls_enabled = self.ctx.config.getboolean('tls', 'enabled', fallback=False)
        host_name = self.ctx.config.get('client', 'server_hostname', fallback='localhost')

        # Search DNS for the hostname.
        try:
            answers = dns.resolver.resolve(host_name, 'A')
            host_ip = answers[0].address
        except:
            host_ip = '127.0.0.1'

        host_ip = self.ctx.config.get('client', 'server_ip', fallback=host_ip)
        host_port = int(self.ctx.config.get('client', 'server_port', fallback=9600))

        # Start socket.
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
            if tls_enabled:
                # Build context.
                certchain = self.ctx.config.get('tls', 'chain')
                context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
                context.load_verify_locations(certchain)
                with context.wrap_socket(sock, server_hostname=host_name) as ssock:
                    ssock.connect((host_ip, host_port))
                    self.run_client_thread(ssock)
            else:
                sock.connect((host_ip, host_port))
                self.run_client_thread(sock)
