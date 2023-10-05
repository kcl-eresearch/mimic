import re
from flask import Flask, request, render_template
from mimic.client.client import MimicClient

class MimicClientFlask:
    def __init__(self, ctx):
        self.ctx = ctx

        # Create the app.
        app = Flask(__name__)
        self.app = app

        @app.route('/')
        def index():
            display_name = request.environ.get('MELLON_displayname')
            return render_template('index.html', display_name=display_name)

        @app.route('/spawn')
        def spawn():
            username = request.environ.get('MELLON_uid')
            if not username:
                return {
                    'result': 'failure'
                }

            # Sanitise.
            regex = re.compile('[^a-zA-Z0-9]')
            username = regex.sub('', username)

            # Spawn.
            client = MimicClient(self.ctx)
            if client.spawn(username):
                return {
                    'result': 'success',
                    'url': "%s/users/%s/" % (self.ctx.config.get('client', 'url'), username)
                }

            return {
                'result': 'failure'
            }
    
    def run(self):
        host = self.ctx.config.get('client', 'host', fallback='localhost')
        port = int(self.ctx.config.get('client', 'port', fallback=9601))
        self.app.run(host=host, port=port)
