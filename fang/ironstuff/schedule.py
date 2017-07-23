import threading
from ultils import stringhelpers
from api.request_helpers import RequestHelpers
from api.request_url import RequestURL
from fang.ironstuff.irondiscovery import IronDiscovery
import time
from datetime import datetime

from database.impl.table_impl import TABLEImpl


class Schedule(threading.Thread):
    ''' Schedule threading'''
    def __init__(self, name=None, mop_data=None, template_data=None, dict_schedule=None, is_stop=None,
                 mechanism=None, schedule_id = 0, queue=None, output_mapping=None):
        threading.Thread.__init__(self)
        self.name = name
        self.mop_data = mop_data
        self.template_data = template_data
        self.dict_schedule = dict_schedule
        self.is_stop = is_stop
        self.mechanism = mechanism
        self.requestURL = RequestURL()
        self._request = RequestHelpers()
        self.is_waiting = True
        self.schedule_id = schedule_id
        self.queue = queue
        self.output_mapping = output_mapping


    def run(self):
        try:
            #---------------------------- waiting time for time start ------------------------------------------------
            while self.is_waiting:
                run_time = self.mop_data['run_datetime'].split("-")[1].strip()
                time_start = datetime.strptime(run_time, '%H:%M').time()
                time_current = datetime.strptime("%d:%d"%(datetime.now().hour, datetime.now().minute), "%H:%M").time()

                if time_current >= time_start:
                    self.is_waiting = False
            #---------------------------------------------------------------------------------------------------------

            while not self.is_stop:
                # -------------------- run device from mop -------------------------------------------
                array_device_mop = self.mop_data['devices']

                '''run_devices = {}
                for item in array_device_mop:
                    self._request.url = self.requestURL.URL_GET_DEVICE_DETAIL % (int(item)) # get device detail
                    device = self._request.get().json()
                    run_devices[str(item)] = device['role']

                self.template_data['run_devices'] = run_devices'''

                key_mop = 'main_schedule_%d' % (self.mop_data['mop_id'])


                try:
                    table_id = int(self.mop_data['save_to_table'])
                    tableImpl = TABLEImpl()
                    table_name = tableImpl.get(table_id)['table_name']

                    irondiscovery = IronDiscovery("IRONMAN-Thread-Template-%s" % (self.mop_data['mop_id']),
                                                  self.template_data, {}, self.mop_data['mop_id'], table_name, self.output_mapping)
                    # insert to queue discovery
                    self.queue.put(irondiscovery)

                    # irondiscovery.start()
                    # irondiscovery.join()

                    if self.mechanism.upper() == 'MANUAL':
                        self.is_stop = True
                        del self.dict_schedule[key_mop]
                    else:
                        weekday = datetime.now().strftime('%A')
                        if weekday not in list(self.mop_data['day_in_week']):
                            del self.dict_schedule[key_mop]
                            self.is_stop = True
                        else:
                            while True:
                                if irondiscovery.done == True:
                                    #stringhelpers.info('[IRON][DISCOVERY][WAITING][%d minutes][%s]' % (
                                    #int(self.mop_data['return_after']), self.name))

                                    stringhelpers.info('[IRON][DISCOVERY][WAITING][%d minutes][%s]' % (
                                    int(5), self.name))

                                    #time.sleep(int(self.mop_data['return_after']) * 60)
                                    time.sleep(5 * 60)
                                    break

                except Exception as _exError:
                    stringhelpers.err("[ERROR] %s" % (_exError))




        except Exception as error:
            stringhelpers.err("[ERROR] %s %s" % (self.name, error))


