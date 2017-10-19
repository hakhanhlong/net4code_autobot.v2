import threading
from time import time, sleep
from datetime import datetime

from ultils import stringhelpers


class HeartBeat(threading.Thread):

    def __init__(self, is_stop, socketio):
        threading.Thread.__init__(self)
        self.is_stop = is_stop
        self.time_start = time()
        self.time_to_live = time()
        self.io = socketio

    def run(self):
        while not self.is_stop:
            try:
                self.time_to_live = time() - self.time_start
                self.io.emit('autobot_heartbeat_state', self.time_to_live)
                sleep(1)
            except Exception as e:
                stringhelpers.err("HEARTBEAT THREAD ERROR %s" % (e))
