from flask import Flask, request, redirect
from mimic.server.client import MimicServerClient

class MimicServerFlask:
    def __init__(self, ctx, server):
        self.ctx = ctx
        self.server = server

        # Create the app.
        app = Flask(__name__)
        self.app = app

        @app.route('/')
        def index():
            if self.server.active_clients == {} or self.server.active_clients == None:
                return 'No servers available.', 503

            # Simple round robin load balancing.
            active_clients = [c for c in self.server.active_clients.values() if c.is_alive()]
            active_clients.sort(key=lambda x: x.load)
            if not active_clients:
                return 'No servers available.', 503

            chosen_client = active_clients[0]
            chosen_client.load += 1
            return redirect(chosen_client.url)
    
        def verify_token():
            token = request.form.get('token')
            return token == ctx.config.get('server', 'psk')

        @app.route('/api/client/register', methods=['POST'])
        def register_client():
            if not verify_token():
                return 'Invalid token', 403
            client_name = request.form.get('name')
            client_url = request.form.get('url')
            client = MimicServerClient(self.ctx, client_name, client_url)
            self.server.register_client(client)
            return 'OK'
        
        @app.route('/api/client/unregister', methods=['POST'])
        def unregister_client():
            if not verify_token():
                return 'Invalid token', 403
            client_name = request.form.get('name')
            self.server.unregister_client(client_name)
            return 'OK'

        @app.route('/api/client/heartbeat', methods=['POST'])
        def heartbeat_client():
            if not verify_token():
                return 'Invalid token', 403
            client_name = request.form.get('name')
            client_load = request.form.get('load')
            self.server.heartbeat_client(client_name, client_load)
            return 'OK'
    
    def run(self):
        host = self.ctx.config.get('client', 'host', fallback='localhost')
        port = int(self.ctx.config.get('client', 'port', fallback=9601))
        self.app.run(host=host, port=port)
