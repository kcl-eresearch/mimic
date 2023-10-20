import re
from flask import Flask, request, render_template
from mimic.client.client import MimicClient


class MimicClientFlask:
    def __init__(self, ctx):
        self.ctx = ctx

        # Create the app.
        app = Flask(__name__)
        self.app = app

        @app.route("/")
        def index():
            display_name = request.headers.get("X-Webauth-Name")
            return render_template("index.html", display_name=display_name)

        @app.route("/spawn")
        def spawn():
            username = request.headers.get("X-Webauth-User") or ""
            # Sanitise.
            regex = re.compile("[^a-zA-Z0-9]")
            username = regex.sub("", username)
            if not username:
                return {"result": "failure"}, 403

            # Spawn.
            if username:
                client = MimicClient(self.ctx)
                if client.spawn(username):
                    return {"result": "success", "url": self.get_redirect_url(username)}

            return {"result": "failure"}, 500

    def get_redirect_url(self, username):
        redirecturl = self.ctx.config.get("client", "url")
        slash = "/" if redirecturl[-1] != "/" else ""
        redirecturl = "%s%susers/%s/" % (redirecturl, slash, username)
        return redirecturl

    def run(self):
        host = self.ctx.config.get("client", "host", fallback="localhost")
        port = int(self.ctx.config.get("client", "port", fallback=9601))
        self.app.run(host=host, port=port)
