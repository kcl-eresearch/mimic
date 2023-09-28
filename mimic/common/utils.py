#
# Mimic - Deploy web applications as users
#

import time

def close_thread(thread, timeout=1):
    if thread.is_alive():
        thread.terminate()
        time.sleep(timeout)
        if thread.is_alive():
            thread.kill()
