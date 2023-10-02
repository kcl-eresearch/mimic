#!/usr/bin/python

import argparse
import os
import subprocess
import time
from pwd import getpwnam

def _run_as_user(pw_uid, pw_gid):
    def result():
        os.setgid(pw_gid)
        os.setuid(pw_uid)
    return result

def run_as_user(username, command):
    pwnam = getpwnam(username)
    user_home_path = "/users/%s" % username
    process = subprocess.Popen(
        command, preexec_fn=_run_as_user(pwnam.pw_uid, pwnam.pw_gid), cwd=user_home_path, env={
            'HOME': user_home_path,
            'USER': username,
        }
    )
    return process.wait()

# Parse args.
parser = argparse.ArgumentParser(description='Mimic a web app.')
parser.add_argument("app")
parser.add_argument("username")
args = parser.parse_args()

# Mimic the app.
supported_apps = ['vscode', 'jupyterlab'] # + ['php-fpm']

if args.app not in supported_apps:
    print("Unsupported app: %s" % args.app)
    exit(1)

# Create /var/run/mimic/<USER>
path = "/var/run/mimic/%s" % args.username
if not os.path.exists(path):
    userpwnam = getpwnam(args.username)
    wwwpwnam = getpwnam("www-data")
    uid = os.getuid()
    os.makedirs(path, 0o750)
    os.chown(path, userpwnam.pw_uid, wwwpwnam.pw_gid)

wrote_httpd_conf = False

if args.app == 'php-fpm':
    pool_def = "/etc/php/8.1/fpm/pool.user.d/%s.conf" % args.username
    print("Mimicking php-fpm app for user %s" % args.username)
    print("Pool definition: %s" % pool_def)

    # Open template file.
    with open("/usr/share/mimic/templates/php81-fpm.tpl", "r") as f:
        template = f.read()
    
    # Replace username.
    template = template.replace("{{username}}", args.username)

    # Write pool definition.
    with open(pool_def, "w") as f:
        f.write(template)
    
    # Restart php-fpm.
    print("Restarting php-fpm...")
    os.system("systemctl reload php8.1-fpm")

if args.app == 'vscode':
    print("Mimicking vscode app for user %s" % args.username)

    # Write apache config for this user.
    # I hate this, but apache doesnt let you use variables for unix socket paths which I guess
    # is for "security" but still... this is ugly.
    path = "/etc/apache2/mimic.conf.d/vscode/%s.conf" % args.username
    if not os.path.exists(path):
        with open(path, "w") as f:
            f.write("<Location /users/%s/>\n" % args.username)
            f.write("ProxyPass unix:/var/run/mimic/%s/vscode.sock|http://code-%s/ upgrade=websocket\n" % (args.username, args.username))
            f.write("ProxyPassReverse unix:/var/run/mimic/%s/vscode.sock|http://code-%s/\n" % (args.username, args.username))
            f.write("MellonCond \"uid\" \"%s\"\n" % args.username)
            f.write("</Location>\n")

            wrote_httpd_conf = True

    # Start an instance.
    os.system("systemctl start code-server@%s" % args.username)

    # Wait for it to come up.
    time.sleep(10)

if args.app == 'jupyterlab':
    print("Mimicking jupyterlab app for user %s" % args.username)

    # Write apache config for this user.
    # I hate this, but apache doesnt let you use variables for unix socket paths which I guess
    # is for "security" but still... this is ugly.
    path = "/etc/apache2/mimic.conf.d/jupyterlab/%s.conf" % args.username
    if not os.path.exists(path):
        with open(path, "w") as f:
            f.write("<Location /users/%s/>\n" % args.username)
            f.write("ProxyPass unix:/var/run/mimic/%s/jupyterlab.sock|http://jupyterlab-%s/users/%s/ upgrade=websocket\n" % (args.username, args.username, args.username))
            f.write("ProxyPassReverse unix:/var/run/mimic/%s/jupyterlab.sock|http://jupyterlab-%s/users/%s/\n" % (args.username, args.username, args.username))
            f.write("MellonCond \"uid\" \"%s\"\n" % args.username)
            f.write("</Location>\n")

            wrote_httpd_conf = True
    
    # Configure venv if needed.
    user_home_path = "/users/%s" % args.username
    venv_path = "%s/.kcl-mimic/conda" % user_home_path
    if not os.path.exists(venv_path):
        run_as_user(args.username, [
            "/usr/bin/sh",
            "/software/mimic/Miniconda3-latest-Linux-x86_64.sh",
            "-b", "-f", "-p", venv_path
        ])
    
    # Install jupyterlab if needed.
    venv_bin_path = "%s/bin" % venv_path
    if not os.path.exists("%s/jupyter" % venv_bin_path):
        run_as_user(args.username, [
            "%s/conda" % venv_bin_path,
            "install",
            "-y",
            "-c",
            "conda-forge",
            "jupyterlab"
        ])

    # Start an instance.
    os.system("systemctl start jupyterlab@%s" % args.username)

    # Wait for it to come up.
    time.sleep(10)

if wrote_httpd_conf:
    os.system("/usr/local/sbin/apache_safe_reload")

exit(0);
