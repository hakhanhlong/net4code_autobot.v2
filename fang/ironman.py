import threading
import time
from datetime import datetime
from ultils import stringhelpers


from api.request_helpers import RequestHelpers
from api.request_url import RequestURL
from fang.ironstuff.schedule import Schedule

import queue

from fang.ironstuff.ironqueue import IronQueue





class IronManager(threading.Thread):
    """ Thread management ironman thread """
    def __init__(self, name, is_stop):
        threading.Thread.__init__(self)
        self.name = name
        self.is_stop = is_stop
        self.counter = 0
        self.requestURL = RequestURL()


    def run(self):
        _request = RequestHelpers()
        dict_schedule = dict()
        dict_schedule_queue = dict()
        list_time = list()
        queue_discovery = queue.Queue()

        # run queue listining discovery ------------------------------------------------------------------------------
        _ironQueue = IronQueue(queue_discovery)
        _ironQueue.start()
        # ------------------------------------------------------------------------------------------------------------

        while not self.is_stop:
            try:
                self.counter = self.counter + 1
                # -------------- IRONMAN RUN SCHEDULE ----------------------------------------------------------------
                stringhelpers.print_bold("IRONMAN SCHEDULE RUN NUMBER: " + str(self.counter), "\n")
                # get current day name
                #weekday = datetime.now().strftime('%A')
                #_request.url = self.requestURL.IRONMAN_URL_GET_SCHEDULE % (weekday)
                _request.url = self.requestURL.IRONMAN_URL_GET_MOP_RUN_IRON
                _list_schedules = _request.get().json()
                if len(_list_schedules) > 0:
                    for x in _list_schedules:
                        stringhelpers.print_bold("IRONMAN RUN MOP: " + str(x['mop_id']), "\n")
                        key_mop = 'main_schedule_%d' % (int(x['mop_id']))
                        mop_id = int(x['mop_id'])
                        mechanism = x['run_type']
                        run_time = x['run_datetime'].split("-")[1].strip()
                        dict_schedule_queue[str(x['mop_id'])] = run_time
                        if dict_schedule.get(key_mop, None) is not None:
                            pass
                        else:
                            list_time.append(run_time)
                            _sub_mops = x.get('sub_mops', None)
                            dict_schedule[key_mop] = key_mop
                            schedule = Schedule("SCHEDULE-%d" % (mop_id), x, _sub_mops,  dict_schedule, False,
                                                mechanism, mop_id, queue_discovery, x['output_mapping'])
                            schedule.start()
                            time.sleep(2)
            except Exception as e:
                stringhelpers.print_bold("IRONMAN SCHEDULE [ERROR]: " + str(e), "\n")

            time.sleep(5)

        # stop iron queue ----------------------------------------------------------------------------------------------
        _ironQueue.stop()
        #---------------------------------------------------------------------------------------------------------------

    def stop(self):
        self.is_stop = True