import threading
from ultils import stringhelpers
from api.request_helpers import RequestHelpers
from api.request_url import RequestURL
from fang.ironstuff.irondiscovery import IronDiscovery
from fang.ironstuff.iron_mop_discovery import Iron_Mop_Discovery

import time
from datetime import datetime

from database.impl.table_impl import TABLEImpl


class Schedule(threading.Thread):
    ''' Schedule threading'''
    def __init__(self, name=None, mop_data=None, sub_mops=None, dict_schedule=None, is_stop=None,
                 mechanism=None, mop_id = 0, queue=None, output_mapping=None):
        threading.Thread.__init__(self)
        self.name = name
        self.mop_data = mop_data
        self.sub_mops = sub_mops
        self.dict_schedule = dict_schedule
        self.is_stop = is_stop
        self.mechanism = mechanism
        self.requestURL = RequestURL()
        self._request = RequestHelpers()
        self.is_waiting = True
        self.mop_id = mop_id
        self.queue = queue
        self.output_mapping = output_mapping
        self.database_mop = dict()
        self.trying_waiting_done = 1000


    def run(self):
        try:
            count_timesleep = 0
            dict_version_container = dict()
            #---------------------------- waiting time for time start ------------------------------------------------
            while self.is_waiting:
                run_time = self.mop_data['run_datetime'].split("-")[1].strip()
                time_start = datetime.strptime(run_time, '%H:%M').time()
                time_current = datetime.strptime("%d:%d"%(datetime.now().hour, datetime.now().minute), "%H:%M").time()

                if time_current >= time_start:
                    self.is_waiting = False
                else:
                    stringhelpers.info('\n[IRON][DISCOVERY][START RUNNING TIME][%s]' % (str(self.mop_data['run_datetime'])))
            #-----------------------------------------------------------------------------------------------------------
            while not self.is_stop:
                # -------------------- run device from mop -------------------------------------------------------------
                key_mop = 'main_schedule_%d' % (int(self.mop_data['mop_id']))
                try:
                    table_id = int(self.mop_data['save_to_table'])
                    tableImpl = TABLEImpl()
                    table_name = tableImpl.get(table_id)['table_name']
                    key_merge = self.mop_data.get('key_merge', None);
                    count_number = 0
                    arr_manager_discovery = []


                    len_submops = len(self.sub_mops) - 1
                    for sub_mop_item in self.sub_mops:

                        sub_no = int(sub_mop_item.get('subNo', 0))

                        irondiscovery = Iron_Mop_Discovery("IRONMAN-Thread-Template-%s" % (str(self.mop_id)),
                                                      sub_mop_item, {}, self.mop_id, table_name, self.output_mapping[str(sub_no)],
                                                      key_merge, sub_no, dict_version_container, len_submops)
                        # insert to queue discovery
                        self.queue.put(irondiscovery)
                        arr_manager_discovery.append(irondiscovery)
                        count_number = count_number + 1
                        stringhelpers.info('\n[ENQUEUE] - > [IRON][DISCOVERY][RUNNING][MOP_ID: %s][SUB_MOP_NAME: %s]' % (str(self.mop_id), sub_mop_item['name']))


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
                                count = 0
                                count_trying_waiting = 0
                                for discovery_item in arr_manager_discovery:
                                    if discovery_item.done == True:
                                        count = count + 1
                                    time.sleep(0.2)
                                if count == len(arr_manager_discovery):
                                    #count_timesleep = count_timesleep + 1
                                    #_mop_details = self.database_mop.get(str(self.mop_id), None)
                                    #if _mop_details is None:
                                        #----------------------------- get detail sub mop --------------------------------------------------------------------
                                    self._request.url = self.requestURL.IRONMAN_URL_GET_MOP_DETAIL % (str(self.mop_id))
                                    _mop_details = self._request.get().json()
                                    #    self.database_mop[str(self.mop_id)] = _mop_details
                                    #self._request.url = self.requestURL.IRONMAN_URL_GET_MOP_DETAIL % (str(self.mop_id))
                                    #_mop_details = self._request.get().json()

                                    sub_mops = _mop_details.get('sub_mops', None)
                                    if sub_mops is not None:
                                        self.sub_mops = sub_mops
                                        stringhelpers.info('\n[IRON][DISCOVERY][GET_MOP_DETAIL_FOR_LOOP][MOP_ID:%s][%s]' % (self.mop_id, self.name))
                                    #--------------------------------------------------------------------------------------------------------------
                                    stringhelpers.info('\n[IRON][DISCOVERY][WAITING][%d minutes][%s]' % (int(self.mop_data['return_after']), self.name))
                                    #stringhelpers.countdown(int(self.mop_data['return_after']) * 60)
                                    stringhelpers.countdown(60)
                                    #time.sleep(int(self.mop_data['return_after']) * 60)
                                    #time.sleep(2 * 60)

                                    break
                                time.sleep(1)
                except Exception as _exError:
                    stringhelpers.err("[ERROR] %s" % (_exError))

        except Exception as error:
            stringhelpers.err("[ERROR] %s %s" % (self.name, error))


