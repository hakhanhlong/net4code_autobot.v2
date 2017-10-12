import threading
from time import time, sleep
from datetime import datetime

from ultils import stringhelpers


class HeartBeat(threading.Thread):

    def __int__(self, is_stop, socketio):
        self.is_stop = is_stop
        self.time_start = time()
        self.time_to_live = time()
        self.io = socketio

    def run(self):
        while not self.is_stop:
            try:
                sleep(60)
                self.time_to_live = time() - self.time_start

            except Exception as e:
                stringhelpers.err("HEARTBEAT THREAD ERROR %s" % (e))
