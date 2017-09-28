import threading
import time
from datetime import datetime
from ultils import stringhelpers


from api.request_helpers import RequestHelpers
from api.request_url import RequestURL

from api.sockbot_api_helpers import SockbotAPIHelpers
from api.sockbot_api_url import SockbotAPIURL

from fang.ironstuff.schedule import Schedule

import queue

from fang.ironstuff.ironqueue import IronQueue
import os







class IronManager(threading.Thread):
    """ Thread management ironman thread """
    def __init__(self, name, is_stop, socketio, socketio_iron):
        threading.Thread.__init__(self)
        self.name = name
        self.is_stop = is_stop
        self.counter = 0
        self.requestURL = RequestURL()
        self.socketio = socketio
        self.socketio_iron = socketio_iron
        self._sockbotAPIHelpers = SockbotAPIHelpers()
        self._sockbotAPIURL = SockbotAPIURL()



    def run(self):
        _request = RequestHelpers()
        dict_schedule = dict()
        dict_schedule_queue = dict()
        list_time = list()
        queue_discovery = queue.Queue()

        # run queue listining discovery ------------------------------------------------------------------------------
        _ironQueue = IronQueue(queue_discovery, self.socketio, self.socketio_iron)
        _ironQueue.start()

        # ------------------------------------------------------------------------------------------------------------

        while not self.is_stop:
            try:
                self.counter = self.counter + 1
                arr_schedule_manage = []
                # -------------- IRONMAN RUN SCHEDULE ----------------------------------------------------------------
                #stringhelpers.print_bold("IRONMAN SCHEDULE RUN NUMBER: " + str(self.counter), "\n")
                # get current day name
                #weekday = datetime.now().strftime('%A')
                #_request.url = self.requestURL.IRONMAN_URL_GET_SCHEDULE % (weekday)
                _request.url = self.requestURL.IRONMAN_URL_GET_MOP_RUN_IRON
                _list_schedules = _request.get().json()
                if len(_list_schedules) > 0:
                    for x in _list_schedules:
                        key_mop = 'main_schedule_%d' % (int(x['mop_id']))
                        mop_id = int(x['mop_id'])
                        mechanism = x['run_type']
                        run_time = x['run_datetime'].split("-")[1].strip()
                        dict_schedule_queue[str(x['mop_id'])] = run_time
                        if dict_schedule.get(key_mop, None) is not None:
                            pass
                        else:
                            stringhelpers.info("IRONMAN RUNNING MOP: " + str(x['mop_id']), "\n")
                            list_time.append(run_time)
                            _sub_mops = x.get('sub_mops', None)
                            dict_schedule[key_mop] = key_mop


                            schedule = Schedule("SCHEDULE-%d" % (mop_id), x, _sub_mops,  dict_schedule, False,
                                                mechanism, mop_id, queue_discovery, x['output_mapping'], self.socketio, self.socketio_iron)
                            arr_schedule_manage.append(schedule)

                            #-----------------------process call api sockbot mop---------------------------------------

                            params_mops = dict()
                            params_mops['name'] = x['name']
                            params_mops['app_secret_id'] = os.environ.get('SOCKBOT_APPCLIENT_SECRET')
                            params_mops['mop_id'] = x['mop_id']
                            params_mops['status'] = 'RUNNING'
                            params_mops['belong'] = 'IRONMAN'
                            params_mops['command'] = 'STARTED'
                            submops = []
                            for x_sub in _sub_mops:
                                arr_devices = []
                                for k,v in x_sub['devices'].items():
                                    arr_devices.append({'mop_id':x['mop_id'],'device_id': v['device_id'],'vendor':'%s|%s'%(v['vendor'],v['os']),'port':v['port']})
                                submops.append({'subNo':x_sub['subNo'], 'name':x_sub['name'], 'devices': arr_devices,
                                                'num_devices':len(arr_devices)})
                            params_mops['submops'] = submops
                            self._sockbotAPIHelpers.url = self._sockbotAPIURL.SOCKBOT_API_CREATE_MOP
                            self._sockbotAPIHelpers.params = params_mops
                            self._sockbotAPIHelpers.post_json()

                            #------------------------------------------------------------------------------------------

                if len(arr_schedule_manage) > 0:
                    for schedule in arr_schedule_manage:
                        schedule.start()

                    arr_schedule_manage.clear()
            except Exception as e:
                stringhelpers.print_bold("IRONMAN SCHEDULE [ERROR]: " + str(e), "\n")

            time.sleep(60)

        # stop iron queue ----------------------------------------------------------------------------------------------
        _ironQueue.stop()
        #---------------------------------------------------------------------------------------------------------------

    def stop(self):
        self.is_stop = True