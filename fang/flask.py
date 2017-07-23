import threading
from time import time, sleep
from ultils import stringhelpers
from api.request_helpers import RequestHelpers
from api.request_url import RequestURL

from .flaskstuff.flask_mop import FlaskSubMop

from datetime import datetime



class FlaskManager(threading.Thread):
    """ Thread management flask thread """
    def __init__(self, name, is_stop):
        threading.Thread.__init__(self)
        self.name = name
        self.is_stop = is_stop
        self.counter = 0
        self.requestURL = RequestURL()
        self._request = RequestHelpers()


    def update_mop_status(self, status, mop_id = None, start_time = None, duration=None):
        # ---------------update mega_status to action------------------------------------------------
        self._request.url = self.requestURL.FLASK_URL_MOP_UPDATE % (mop_id)
        dict_update = {'flash_status': status}
        if status == 'running':
            dict_update['start_time'] = datetime.now().strftime("%Y-%m-%d %H:%M")
        if status == 'done' or status == 'rolledback':
            dict_update['end_time'] = datetime.now().strftime("%Y-%m-%d %H:%M")
            dict_update['duration_time'] = '%.2f' % (duration - start_time)

        self._request.params = dict_update
        self._request.put()


    def run(self):
        _request = RequestHelpers()
        dict_template = dict()
        while not self.is_stop:
            try:
                self.counter = self.counter + 1
                stringhelpers.print_bold("Archieving info FLASK number: %d" % self.counter)
                #-------------- FLASK RUN MOP ----------------------------------------------------------------
                _request.url = self.requestURL.FLASK_URL_MOP
                #_list_templates = _request.get().json()
                _list_mops = _request.get().json()
                if len(_list_mops) > 0:
                    for x in _list_mops:
                        mop_id = int(x['mop_id'])
                        key_mop = 'flask_mop_%d' % (mop_id)

                        if dict_template.get(key_mop, None) is not None:
                            pass
                        else:
                            sub_mops = x['sub_mops']
                            dict_template[key_mop] = key_mop

                            status = 'running'
                            self.update_mop_status(status, mop_id)
                            start_time = time()
                            for item_mop in sub_mops:
                                flask_sub_mop = FlaskSubMop("FLASK-Thread-MOP-%d" % (mop_id), item_mop, mop_id)
                                flask_sub_mop.start()
                                status = flask_sub_mop.join()

                            self.update_mop_status(status, mop_id, start_time, time())
                            #del dict_template[key_mop]


                # ---------------------------------------------------------------------------------------------------------
                sleep(30)




            except Exception as e:
                stringhelpers.err("FLASK MAIN THREAD ERROR %s" % (e))
            except ConnectionError as errConn:
                stringhelpers.err("FLASK CONNECT API ERROR %s" % (errConn))



    '''def run(self):
        _request = RequestHelpers()
        dict_template = dict()
        while not self.is_stop:
            try:
                self.counter = self.counter + 1
                stringhelpers.print_bold("Archieving info FLASK number: %d" % self.counter)


                #-------------- FLASK RUN MOP --------------------------------------------------------------------------
                _request.url = self.requestURL.FLASK_URL_MOP
                #_list_templates = _request.get().json()
                _list_mops = _request.get().json()
                if len(_list_mops) > 0:
                    for x in _list_mops:
                        key_mop = 'template_%d' % (x['mop_id'])
                        mop_id = x['mop_id']
                        if dict_template.get(key_mop, None) is not None:
                            pass
                        else:
                            _request.url = self.requestURL.MEGA_URL_TEMPLATE_DETAIL % (x['template_id'])
                            _template = _request.get().json()
                            #-------------------- run device from mop --------------------------------------------------
                            array_device_mop = x['devices']
                            run_devices = {}
                            for item in array_device_mop:
                                run_devices[str(item)] = "MOP"

                            _template['run_devices'] = run_devices
                            #-------------------------------------------------------------------------------------------
                            try:
                                _template['run_args'] = x['run_args']
                                _template['rollback_args'] = x['rollback_args']
                            except:
                                pass

                            dict_template[key_mop] = key_mop
                            flask_template = FlaskTemplate("FLASK-Thread-Template-%s" % (x['template_id']), _template, dict_template, mop_id)
                            flask_template.start()


                # ------------------------------------------------------------------------------------------------------
                time.sleep(30)




            except Exception as e:
                stringhelpers.err("FLASK MAIN THREAD ERROR %s" % (e))
            except ConnectionError as errConn:
                stringhelpers.err("FLASK CONNECT API ERROR %s" % (errConn))
    '''

    def stop(self):
        self.is_stop = True
