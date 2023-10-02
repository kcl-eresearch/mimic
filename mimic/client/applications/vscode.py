#
# Mimic - Deploy web applications as users
#

import os
import time

from mimic.client.applications import App

class AppVSCode(App):
    def run(self, username) -> None:
        print("Mimicking vscode app for user %s" % username)

        # Write apache config for this user.
        # I hate this, but apache doesnt let you use variables for unix socket paths which I guess
        # is for "security" but still... this is ugly.
        path = "/etc/apache2/mimic.conf.d/vscode/%s.conf" % username
        if not os.path.exists(path):
            with open(path, "w") as f:
                f.write("<Location /users/%s/>\n" % username)
                f.write("ProxyPass unix:/var/run/mimic/%s/vscode.sock|http://code-%s/ upgrade=websocket\n" % (username, username))
                f.write("ProxyPassReverse unix:/var/run/mimic/%s/vscode.sock|http://code-%s/\n" % (username, username))
                f.write("MellonCond \"uid\" \"%s\"\n" % username)
                f.write("</Location>\n")

                os.system("/usr/local/sbin/apache_safe_reload")

        # Start an instance.
        os.system("systemctl start code-server@%s" % username)
    
    def check_heartbeat(self, username) -> bool:
        heartbeat = "/users/%s/.local/share/code-server/heartbeat" % username
        if os.path.exists(heartbeat) and self.is_heartbeat_active(heartbeat):
            return
        self.stop()

    def stop(self, username) -> None:
        print("Stopping vscode app for user %s" % username)

        # Stop an instance.
        os.system("systemctl stop code-server@%s" % username)

        # Remove apache config for this user.
        path = "/etc/apache2/mimic.conf.d/vscode/%s.conf" % username
        if os.path.exists(path):
            os.remove(path)
            os.system("/usr/local/sbin/apache_safe_reload")

    def wait_for_startup(self) -> None:
        time.sleep(10)
