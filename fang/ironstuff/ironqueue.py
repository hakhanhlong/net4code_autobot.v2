import threading
from ultils import stringhelpers
import time

class IronQueue(threading.Thread):

    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.is_stop = False

    def run(self):
        try:
            while not self.is_stop:
                if not self.queue.empty():
                    discovery = self.queue.get()
                    discovery.start()
                    discovery.join()
                time.sleep(0.3) # delay 1s
        except Exception as error:
            stringhelpers.err("ERROR [IRONQUEUE]: {}".format(error))

    def stop(self):
        self.is_stop = True
