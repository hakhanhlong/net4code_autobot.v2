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
                    time.sleep(2)  # delay 2s
                    stringhelpers.err("[START] -> QUEUE  %s [MOP ID]: %s\n" % (discovery.name, discovery.mop_id))
                    done = discovery.join()
                    stringhelpers.err("[DONE] -> QUEUE  %s [MOP ID]: %s\n" % (discovery.name, discovery.mop_id))
                time.sleep(1) # delay 1s
        except Exception as error:
            stringhelpers.err("ERROR [IRONQUEUE]: {}".format(error))

    def stop(self):
        self.is_stop = True
