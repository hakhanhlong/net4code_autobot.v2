import threading
from ultils import stringhelpers
import time

class IronQueue(threading.Thread):

    def __init__(self, queue, socketio, socketio_iron):
        threading.Thread.__init__(self)
        self.queue = queue
        self.is_stop = False

        self.socketio = socketio
        self.socketio_iron = socketio_iron


    def run(self):
        try:
            while not self.is_stop:
                if not self.queue.empty():
                    discovery = self.queue.get()

                    dict_mop_state = {
                        'submop': "submop_{}_{}".format(discovery.mop_id, discovery.submop_index),
                        'text': 'RUNNING'
                    }

                    discovery.start()
                    self.socketio_iron.emit('running_mop_state', dict_mop_state)
                    time.sleep(2)  # delay 2s
                    stringhelpers.err("[START] -> QUEUE  %s [MOP ID]: %s\n" % (discovery.name, discovery.mop_id))
                    done = discovery.join()
                    dict_mop_state['text'] = 'DONE'
                    self.socketio_iron.emit('running_mop_state', dict_mop_state)
                    stringhelpers.err("[DONE] -> QUEUE  %s [MOP ID]: %s\n" % (discovery.name, discovery.mop_id))
                time.sleep(1) # delay 1s
        except Exception as error:
            stringhelpers.err("ERROR [IRONQUEUE]: {}".format(error))

    def stop(self):
        self.is_stop = True
