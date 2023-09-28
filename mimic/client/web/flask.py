from flask import Flask, render_template

class MimicClientFlask:
    def __init__(self, ctx):
        self.ctx = ctx

        # Create the app.
        app = Flask(__name__)
        self.app = app

        @app.route('/')
        def index():
            return render_template('index.html', display_name='Skylar Kelty')

        @app.route('/spawn')
        def spawn():
            return {
                'result': 'success',
                'url': ''
            }
    
    def run(self):
        host = self.ctx.config.get('client', 'host', fallback='localhost')
        port = int(self.ctx.config.get('client', 'port', fallback=9601))
        self.app.run(host=host, port=port)
