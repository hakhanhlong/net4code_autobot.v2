import threading
from ultils import stringhelpers
from api.request_helpers import RequestHelpers
from api.request_url import RequestURL
from network_adapter.factory_connector import FactoryConnector
from . import func_compare
import json
from datetime import datetime
from time import time, sleep


class FlaskSubMop(threading.Thread):
    """ Thread instance each process template """
    def __init__(self, name, sub_mop, mop_id=None):
        threading.Thread.__init__(self)
        self.sub_mop = sub_mop
        self.mop_id = mop_id
        self.info_fang = self.buildinfo_subtemplates()
        self._request = RequestHelpers()
        self.name = name
        self.requestURL = RequestURL()
        self.result_templates = []
        self.response_mop_status = None


    def mop_status(self, status):
        self.response_mop_status = status

    def join(self):
        threading.Thread.join(self)
        return self.response_mop_status

    def run(self):
        if self.info_fang is not None:
            self.mop_status('running')
            count = 0
            #-----------------------------------------------------------------------------------------------------------
            for fang in self.info_fang['subtemplates']: # fang sub template
                sub_template_name = fang['sub_template_name']
                sub_template_number = count
                subtemplate_thread = SubTemplate(sub_template_name, fang, False, self.result_templates,
                                                 int(fang['mode']), self.mop_id, sub_template_number)
                subtemplate_thread.start()
                dict_template = dict(sub_template_name = sub_template_name, state = subtemplate_thread.join(), fang=fang, mode=int(fang['mode']))
                self.result_templates.append(dict_template)
                count = count + 1



            try:
                self.info_rollback = self.buildinfo_rollback()
                if len(self.info_rollback) > 0:
                    self.result_templates = []
                    try:
                        count = len(self.info_rollback)
                        for fang in self.info_rollback:  # fang sub template
                            self.mop_status('rollingback')
                            sub_template_name = fang['sub_template_name']
                            sub_template_number = fang['sub_template_number']
                            subtemplate_thread = SubTemplate(sub_template_name, fang, True, self.result_templates,
                                                             int(fang['mode']), self.mop_id, sub_template_number)
                            subtemplate_thread.start()
                            dict_template = dict(sub_template_name=sub_template_name, state=subtemplate_thread.join(),fang=fang, mode=int(fang['mode']))
                            self.result_templates.append(dict_template)
                            count = count - 1
                    except:
                        pass

                    if len(self.result_templates) > 0:
                        self.mop_status('rolledback')
                    else:
                        self.mop_status('done')
            except:
                pass
            #-----------------------------------------------------------------------------------------------------------

        else:
            stringhelpers.warn("[%s] FLASK TEMPLATE NOT DATA TO FANG\r\n" % (self.name))
            self.mop_status('error')


    def buildinfo_subtemplates(self):
        data_fang = dict(subtemplates=[])
        # ----------------device list------------------------------------------------------------------------------------
        run_devices = sorted(self.sub_mop['devices'].items(), reverse=False)
        run_mode = self.sub_mop["run_mode"]

        try:

            subtemplate = dict(devices=[])
            for k, v in run_devices:  # get list device id need fang and role of each device
                # k = deviceid
                count_step = 0
                info_fang = {}  # clear each add info
                subtemplate['sub_template_name'] = self.sub_mop['name']

                # ------------ get data chay mode parallel ---------------------------------------------------------
                try:
                    mode = int(run_mode)
                    if mode == 1:
                        subtemplate['mode'] = 1  # not run parallel
                    elif mode == 2:
                        subtemplate['mode'] = 2  # run parallel
                except:
                    pass
                # --------------------------------------------------------------------------------------------------

                try:
                    device_fang = dict(device_id=k) #k = device_id
                    device_id = device_fang['device_id']

                    device_fang['device_info'] = dict(
                        port_mgmt=v['port'],
                        method=v['method'],
                        vendor=v['vendor'],
                        os=v['os'],
                        username=v['username'],
                        password=v['password'],
                        ip_mgmt=v['ip'],
                        device_id=int(v['device_id'])
                    )
                    device_fang['vendor_ios'] = "%s|%s" % (v['vendor'], v['os'])  # vendor+os = e.x: Cisco|ios-xr
                    info_fang['device'] = device_fang
                    dict_action = dict()
                    for action in v['actions']:  # list actions
                        count_step = count_step + 1  # step
                        dict_action[str(count_step)] = action
                    info_fang['actions'] = dict_action
                    subtemplate['devices'].append(info_fang)
                except Exception as _error:
                    stringhelpers.err("FLASK MOP BUILD buildinfo_subtemplates ERROR %s\n\r" % (_error))
            if subtemplate is not None:
                data_fang['subtemplates'].append(subtemplate)
        except:
            pass

        return data_fang

    def buildinfo_rollback(self):
        array_data_rollback = []
        array_keep_device_rollback = []

        if len(self.result_templates) > 0:
            reversed_result = self.result_templates[::-1]
            #reversed_result = self.result_templates
            sub_template_number = len(reversed_result) - 1
            for item in reversed_result:
                dict_template_rollback = dict(devices=[])
                count = 0
                for k, v in (item['state']).items():
                    device_id = k
                    if len(array_keep_device_rollback) > 0:
                        if device_id in array_keep_device_rollback:
                            dict_template_rollback['sub_template_name'] = item['sub_template_name']
                            dict_template_rollback['mode'] = item['mode']
                            dict_template_rollback['sub_template_number'] = sub_template_number
                            for device in item['fang']['devices']:
                                dict_template_rollback['devices'].append(device)
                    if v['final_sub_template'] == False:
                        stringhelpers.info("RUN ROLLBACK - device id: %s, sub_template_name %s" % (device_id, item['sub_template_name'] + "\n\n"))
                        if count == 0:
                            dict_template_rollback['sub_template_name'] = item['sub_template_name']
                            dict_template_rollback['mode'] = item['mode']
                            dict_template_rollback['sub_template_number'] = sub_template_number
                            for device in item['fang']['devices']:
                                dict_template_rollback['devices'].append(device)
                            array_keep_device_rollback.append(device_id)
                            count = 1
                sub_template_number = sub_template_number - 1
                array_data_rollback.append(dict_template_rollback)
        return array_data_rollback




class SubTemplate(threading.Thread):
    '''sub template'''
    def __init__(self, name, subtemplate=None, is_rollback=False, result_templates = None, mode = 0, mop_id=0, sub_template_number=0):
        threading.Thread.__init__(self)
        self.subtemplate = subtemplate
        self.name = name
        self.requestURL = RequestURL()
        self._request = RequestHelpers()
        self.array_state_action = []
        self.dict_state_result = {}
        self.is_rollback = is_rollback
        self.is_check_run_finished = False
        self.result_templates = result_templates
        self.mode = mode
        self.mop_id = mop_id
        self.sub_template_number = sub_template_number


    def update_log(self, logs=None, is_rollback=False, device_id=0, action_id=0):
        if is_rollback == False:
            dict_log_result = dict()
            try:
                self._request.url = self.requestURL.FLASK_URL_MOP_LOGS
                dict_log_result['mop_id'] = self.mop_id

                _dict_data = logs['action_log']['result']['outputs'][str(logs['device_vendor_ios'])]['config']
                # process remove key dict is command_id
                for item in _dict_data: #for each on array
                    try:
                        for k, v in item.items():
                            try:
                                if int(k) > 0:
                                    for sub_k, sub_v in v.items():
                                        item[str(sub_k)] = sub_v
                                    del item[k]
                            except:
                                pass
                    except:
                        pass
                # ------------------------------------------------------------------------------

                dict_log_result['action_log'] = [v for v in _dict_data]
                dict_log_result['device_id'] = device_id
                dict_log_result['action_id'] = action_id
                dict_log_result['final_result_action'] = logs['final_result_action']
                dict_log_result['sub_template_name'] = self.name
                dict_log_result['sub_template_number'] = self.sub_template_number
                dict_log_result['mode'] = 'config'


                self._request.params = dict_log_result
                self._request.post()
                stringhelpers.info(
                    "FLASK TEMPLATE THREAD INFO: %s | THREAD %s" % ("INSERT TEMPLATE LOG SUCCESS [CONFIG]", self.name))

            except ConnectionError as _conErr:
                stringhelpers.err("FLASK TEMPLATE THREAD ERROR: %s | THREAD %s" % (_conErr, self.name))
            # ---------------------------------------------------------------------------------------------------
        else:
            dict_log_result = dict()
            try:
                self._request.url = self.requestURL.FLASK_URL_MOP_LOGS
                dict_log_result['mop_id'] = self.mop_id

                _dict_data = logs['action_rollback_log']['result']['outputs'][str(logs['device_vendor_ios'])]['rollback']
                # process remove key dict is command_id
                for item in _dict_data:  # for each on array
                    try:
                        for k, v in item.items():
                            try:
                                if int(k) > 0:
                                    for sub_k, sub_v in v.items():
                                        item[str(sub_k)] = sub_v
                                    del item[k]
                            except:
                                pass
                    except:
                        pass
                # ------------------------------------------------------------------------------
                dict_log_result['action_log'] = [v for v in _dict_data]

                dict_log_result['device_id'] = device_id
                dict_log_result['action_id'] = action_id
                dict_log_result['sub_template_name'] = self.name
                dict_log_result['sub_template_number'] = self.sub_template_number
                dict_log_result['final_result_action'] = logs['final_result_action']
                dict_log_result['mode'] = 'rollback'
                self._request.params = dict_log_result
                self._request.post()
                stringhelpers.info(
                    "FLASK TEMPLATE THREAD INFO: %s | THREAD %s" % ("INSERT TEMPLATE LOG SUCCESS [ROLLBACK]", self.name))

            except ConnectionError as _conErr:
                stringhelpers.err("FLASK TEMPLATE THREAD ERROR: %s | THREAD %s" % (_conErr, self.name))

        #pass

    def excecute(self, data_fang):

        actions = sorted(data_fang['actions'].items(), reverse=False)  # get actions of each sub template # action contain linkedlist
        #--------------------- build info device fang ------------------------------------------------------------------
        device = data_fang['device']['device_info']
        self.dict_state_result[str(device['device_id'])] = {}
        vendor_ios = data_fang['device']['vendor_ios']
        host = device['ip_mgmt']
        port = int(device['port_mgmt'])
        username = device['username']
        password = device['password']
        device_type = device['os']
        method = device['method']  # ssh, telnet
        parameters = {
            'device_type': device_type,
            'host': host,
            'protocol': method.lower(),
            'username': username,
            'password': password,
            'port': port,
            'timeout': 300
        }
        print("FLASK SUBTEMPLATE FANG DEVICE: host=%s, port=%s, devicetype=%s \n" % (parameters['host'], parameters['port'], parameters['device_type']))
        fac = FactoryConnector(**parameters)
        log_output_file_name = "%s.log" % (stringhelpers.generate_random_keystring(10))
        fac = fac.execute_keep_alive(loginfo=log_output_file_name)
        fac.device_id = device['device_id']
        if not fac.is_alive():
            print("CONNECT DEVICE: host=%s, port=%s, devicetype=%s FAIL\n\n" % (parameters['host'], parameters['port'], parameters['device_type']))
            return None
        #---------------------------------------------------------------------------------------------------------------

        # --------------- list dict action command ---------------------------------------------------------------------
        _dict_list_actions = dict()
        # _dict_list_action params = self.data_action['test_args']
        _array_step = []
        if len(actions) > 0:
            for step, action in actions:
                _dict_list_actions[str(step)] = action
                _array_step.append(str(step))  # save step action
        else:
            pass

        # --------------------------------------------------------------------------------------------------------------
        if len(_array_step) > 0:# and self.is_rollback == False:
            compare_final_output = []
            previous_final_output = []

            for step  in _array_step:
                # print(_dict_list_actions[step])
                _action = _dict_list_actions[str(step)]
                action_id = int(_action.get('action_id', 0))
                if action_id > 0:  # command_id > 0

                    try:
                        thread_action_name = "Thread-Action_%s-In-%s" % (action_id, self.name)
                        action_data = _action
                        dependency = int(_action['dependency'])
                        if dependency > 0:  # run need compare
                            dependStep = dependency
                            if (int(_action['condition']) == int(previous_final_output[dependStep - 1])):

                                thread_action = Action(thread_action_name, action_data, action_id, None,
                                                       None, vendor_ios,
                                                       fac, self.is_rollback, log_output_file_name, self.mop_id)
                                thread_action.start()
                                result = thread_action.join()

                                result['action_id'] = action_id
                                result['device_id'] = device['device_id']
                                result['device_vendor_ios'] = vendor_ios

                                previous_final_output.append(result['final_result_action'])
                                self.array_state_action.append(result)
                                self.update_log(result, False, device['device_id'], action_id)
                            else:
                                stringhelpers.err(
                                    "FLASK ACTIONS STEP: %s NOT AVAIABLE WITH FINAL_OUTPUT OF STEP %d| THREAD %s" % (
                                    step, dependStep, self.name))
                                previous_final_output.append(False)
                                continue
                        else:  # dependency == 0
                            thread_action = Action(thread_action_name, action_data, action_id, None,
                                                   None, vendor_ios,
                                                   fac, self.is_rollback, log_output_file_name, self.mop_id)
                            thread_action.start()
                            result = thread_action.join()

                            result['action_id'] = action_id
                            result['device_id'] = device['device_id']
                            result['device_vendor_ios'] = vendor_ios

                            previous_final_output.append(result['final_result_action'])

                            self.array_state_action.append(result)
                            self.update_log(result, False, device['device_id'], action_id)

                            if int(step) > 1:
                                if int(result['final_result_action']) == int(_action.get('condition', 0)):
                                    self.dict_state_result[str(device['device_id'])]["final_sub_template"] = True
                                else:
                                    self.dict_state_result[str(device['device_id'])]["final_sub_template"] = False
                                    compare_final_output = []
                                    break
                    except:
                        stringhelpers.warn("[%s] FLASK TEMPLATE REQUEST DATA ACTION %s FAIL\r\n" % (self.name, action_id))
                else:  # last command in actions check point
                    dependency = int(_action['dependency'])
                    try:
                        if (int(_action['condition']) == int(previous_final_output[dependency - 1])):
                            compare_final_output.append(True)
                        else:
                            compare_final_output.append(False)
                    except:
                        pass


            #------------------------ calculate decide template is True or False ---------------------------------------
            if len(previous_final_output) > 0:
                for x in previous_final_output:
                    if x:
                        self.dict_state_result[str(device['device_id'])]["final_sub_template"] = True
                        self.dict_state_result[str(device['device_id'])]["actions"] = self.array_state_action
                    else:
                        self.dict_state_result[str(device['device_id'])]["final_sub_template"] = False
                        self.dict_state_result[str(device['device_id'])]["actions"] = self.array_state_action
            else:
                self.dict_state_result[str(device['device_id'])]["final_sub_template"] = False
                self.dict_state_result[str(device['device_id'])]["actions"] = self.array_state_action
            #-----------------------------------------------------------------------------------------------------------

            self.array_state_action = []
            fac.remove_file_log(log_output_file_name)
            # stringhelpers.warn(str(self.action_log))
            fac.terminal()  # finished fang command

    def excecute_rollback(self, data_fang):

        actions = sorted(data_fang['actions'].items(), reverse=False)  # get actions of each sub template # action contain linkedlist
        #--------------------- build info device fang -----------------------------------------------------------
        device = data_fang['device']['device_info']
        self.dict_state_result[str(device['device_id'])] = {}
        vendor_ios = data_fang['device']['vendor_ios']
        host = device['ip_mgmt']
        port = int(device['port_mgmt'])
        username = device['username']
        password = device['password']
        device_type = device['os']
        method = device['method']  # ssh, telnet
        parameters = {
            'device_type': device_type,
            'host': host,
            'protocol': method.lower(),
            'username': username,
            'password': password,
            'port': port,
            'timeout': 300
        }
        print("FLASK SUBTEMPLATE FANG DEVICE: host=%s, port=%s, devicetype=%s \n" % (parameters['host'], parameters['port'], parameters['device_type']))
        fac = FactoryConnector(**parameters)
        log_output_file_name = "%s.log" % (stringhelpers.generate_random_keystring(10))
        fac = fac.execute_keep_alive(loginfo=log_output_file_name)
        if not fac.is_alive():
            print("CONNECT DEVICE: host=%s, port=%s, devicetype=%s FAIL\n\n" % (parameters['host'], parameters['port'], parameters['device_type']))
            return None
        #---------------------------------------------------------------------------------------------------------------

        # --------------- list dict action command ---------------------------------------------------------------------
        _dict_list_actions = dict()
        # _dict_list_action params = self.data_action['test_args']
        _array_step = []
        if len(actions) > 0:
            for step, action in actions:
                _dict_list_actions[str(step)] = action
                _array_step.append(str(step))  # save step action
        else:
            pass

        _array_step = _array_step[::-1]
        # --------------------------------------------------------------------------------------------------------------
        if len(_array_step) > 0:# and self.is_rollback == False:
            previous_final_output = []
            for step  in _array_step:
                # print(_dict_list_actions[step])
                _action = _dict_list_actions[str(step)]
                action_id = int(_action.get('action_id', 0))
                if action_id > 0:  # command_id > 0

                    try:
                        thread_action_name = "[ROLLBACK] Thread-Action_%s-In-%s" % (action_id, self.name)
                        action_data = _action

                        thread_action = Action(thread_action_name, action_data, action_id, None,
                                               None, vendor_ios,
                                               fac, self.is_rollback, log_output_file_name, self.mop_id)
                        thread_action.start()
                        result = thread_action.join()
                        result['action_id'] = action_id
                        result['device_id'] = device['device_id']
                        result['device_vendor_ios'] = vendor_ios

                        previous_final_output.append(result['final_result_action'])
                        self.array_state_action.append(result)
                        self.update_log(result, True, device['device_id'], action_id)

                    except:
                        stringhelpers.warn("[ROLLBACK][%s] FLASK TEMPLATE REQUEST DATA ACTION %s FAIL\r\n" % (self.name, action_id))
                else:  # last command in actions check point
                    pass


        self.array_state_action = []
        fac.remove_file_log(log_output_file_name)
        # stringhelpers.warn(str(self.action_log))
        fac.terminal()  # finished fang command




    def run(self):
        try:
            if self.subtemplate is not None:
                threading_array = []
                stringhelpers.info("[INFO]-RUN SUBTEMPLATE: %s" % (self.name))
                filnal_result = []

                #------------------ chay ko song song ------------------------------------------------------------------

                if self.mode == 1: #mode = 1, not parallel

                    for device in self.subtemplate['devices']:
                        device_id = device['device']['device_info']['device_id']

                        if self.is_rollback:
                            self.excecute_rollback(device)
                        else:
                            # -------------- check has run next subtemplate belong previous result subtemplate
                            if len(self.result_templates) > 0:
                                before_result = self.result_templates[len(self.result_templates) - 1]
                                try:
                                    final_sub_template = before_result['state'][str(device_id)]['final_sub_template']
                                    if final_sub_template == False:
                                        print("SUB TEMPLATE: %s FOR DEVICE: %s DON'T CONTINIOUS RUN\n\n" % (
                                        self.name, device_id))
                                        break
                                except:
                                    print(
                                        "SUB TEMPLATE: %s FOR DEVICE: %s DON'T CONTINIOUS RUN\n\n" % (self.name, device_id))
                                    break

                            # ------------------------------------------------------------------------------------------
                            if len(filnal_result) == 0:
                                self.excecute(device)
                            else:
                                if filnal_result[len(filnal_result) - 1] == True:
                                    self.excecute(device)

                        if self.is_rollback == False:
                            try:
                                filnal_result.append(self.dict_state_result[str(device_id)]["final_sub_template"])
                            except:
                                pass
                    #---------------------------------------------------------------------------------------------------
                else: # mode = 2, run parallel

                    #------------------- chay song song ----------------------------------------------------------------
                    for device in self.subtemplate['devices']:
                        device_id = device['device']['device_info']['device_id']
                        if self.is_rollback:
                            _thread = threading.Thread(target=self.excecute_rollback, args=(device,))
                            _thread.start()
                            threading_array.append(_thread)

                            #self.excecute_rollback(device)
                        else:
                            # -------------- check has run next subtemplate belong previous result subtemplate
                            if len(self.result_templates) > 0:
                                before_result = self.result_templates[len(self.result_templates) - 1]
                                try:
                                    final_sub_template = before_result['state'][str(device_id)]['final_sub_template']
                                    if final_sub_template == False:
                                        print("SUB TEMPLATE: %s FOR DEVICE: %s DON'T CONTINIOUS RUN\n\n" % (self.name, device_id))
                                        break
                                except:
                                    print(
                                        "SUB TEMPLATE: %s FOR DEVICE: %s DON'T CONTINIOUS RUN\n\n" % (self.name, device_id))
                                    break

                            # ------------------------------------------------------------------------------------------
                            if len(filnal_result) == 0:
                                _thread = threading.Thread(target=self.excecute, args=(device,))
                                _thread.start()
                                threading_array.append(_thread)
                            else:
                                if filnal_result[len(filnal_result) - 1] == True:
                                    _thread = threading.Thread(target=self.excecute, args=(device,))
                                    _thread.start()
                                    threading_array.append(_thread)

                    if self.is_rollback == False:
                        for x in threading_array:
                            x.join()
                        for device in self.subtemplate['devices']:
                            device_id = device['device']['device_info']['device_id']
                            try:
                                filnal_result.append(self.dict_state_result[str(device_id)]["final_sub_template"])
                            except:
                                pass
                    else: #rollback
                        for x in threading_array:
                            x.join()
                    #-------------------------------------------------------------------------------------------------------



        except Exception as exError:
            stringhelpers.err("[ERROR] RUN SUBTEMPLATE-[%s]: %s" % (self.name, exError))

    def join(self):
        threading.Thread.join(self)
        return self.dict_state_result




''' --------------------------------- Action ------------------------------------------------------------------------'''
class Action(threading.Thread):
    """ Thread instance each process mega """
    def __init__(self, name, data_action = None, action_id = None, params_action=None, param_rollback_action=None,
                 vendor_os=None, session_fang=None, is_rolback=False, file_log=None, mop_id=0):
        threading.Thread.__init__(self)
        self.name = name
        self.data_action = data_action
        self.requestURL = RequestURL()
        self.action_id = action_id
        self._request = RequestHelpers()
        self.data_command = None
        self.action_log = {'result':{'outputs':dict()}}
        self.fang = session_fang
        self.log_output_file_name = file_log
        self.vendor_os = vendor_os

        self.params_action = params_action
        self.param_rollback_action = param_rollback_action

        self.is_rollback = is_rolback

        self.final_result = False
        self.dict_state_result = dict()
        self.mop_id = mop_id



        # sao the nay fuck fuck fuck
    def run(self):
        try:
            key_list_command = self.vendor_os
            self.action_log['result']['outputs'][key_list_command] = {}
            self.action_log['result']['outputs'][key_list_command]['config'] = []
            self.action_log['result']['outputs'][key_list_command]['rollback'] = []

            action_type = self.data_action.get('category_1', None) #thieeu category_1 tra ra tu json
            _list_action_commands = self.data_action['commands']['config']  # list action_command config
            _list_action_rollback = self.data_action['commands']['rollback']  # list action_command rollback

            # --------------- list dict action command -----------------------------------------------------------------
            _dict_list_command = dict()
            _array_step = []
            if len(_list_action_commands) > 0:
                count = 0
                for _command in _list_action_commands:
                    count = count + 1
                    _dict_list_command[str(count)] = _command
                    _array_step.append(str(count))  # save step command
            else:
                pass
            # ----------------------------------------------------------------------------------------------------------
            # --------------- list dict action command rollback---------------------------------------------------------
            _dict_list_command_rollback = dict()
            _array_step_rollback = []
            if len(_list_action_rollback) > 0:
                count = 0
                for _command in _list_action_rollback:
                    count = count + 1
                    _dict_list_command_rollback[str(count)] = _command
                    _array_step_rollback.append(str(count))  # save step command rollback
            else:
                pass
            # ----------------------------------------------------------------------------------------------------------

            '''#############################process command by dependency############################################'''
            if len(_array_step) > 0 and self.is_rollback == False:
                compare_final_output = []
                previous_final_output = []
                for step in _array_step:
                    _command_running = _dict_list_command[step]
                    # if _command_running['dependency'] == '0':
                    command_id = int(_command_running.get('command_id', 0))
                    if command_id > 0:  # command_id > 0
                        dependency = int(_command_running['dependency'])
                        if dependency > 0:  # run need compare
                            dependStep = dependency
                            if (int(_command_running['condition']) == int(previous_final_output[dependStep - 1])):
                                command_type = _command_running.get('type', None)
                                if command_type is not None:
                                    if int(command_type) == 5: #process delay command
                                        output_info = self.process_each_command(command_id, _command_running)
                                        previous_final_output.append(True)
                                    else:
                                        output_info = self.process_each_command(command_id, _command_running)
                                        if output_info is not None:
                                            previous_final_output.append(output_info[str(command_id)]['final_output'])
                                            self.action_log['result']['outputs'][key_list_command]['config'].append(
                                                output_info)
                                            stringhelpers.info(
                                                "\nAction: [%s]-- config step [%s]: filnal-output: %s" % (
                                                self.action_id, step,
                                                str(output_info[str(command_id)]['final_output'])))
                                        else:
                                            previous_final_output.append(False)
                                else:
                                    output_info = self.process_each_command(command_id, _command_running)
                                    if output_info is not None:
                                        previous_final_output.append(output_info[str(command_id)]['final_output'])
                                        self.action_log['result']['outputs'][key_list_command]['config'].append(output_info)
                                        stringhelpers.info("\nAction: [%s]-- config step [%s]: filnal-output: %s" % (self.action_id, step, str(output_info[str(command_id)]['final_output'])))
                                    else:
                                        previous_final_output.append(False)
                            else:
                                stringhelpers.err(
                                    "MEGA ACTIONS STEP: %s NOT AVAIABLE WITH FINAL_OUTPUT OF STEP %d| THREAD %s" % (step, dependStep, self.name))
                                previous_final_output.append(False)
                                continue
                        else:  # dependency == 0
                            command_type = _command_running.get('type', None)
                            if command_type is not None:
                                if int(command_type) == 5:  # process delay command
                                    output_info = self.process_each_command(command_id, _command_running)
                                    previous_final_output.append(True)
                                else:
                                    output_info = self.process_each_command(command_id, _command_running)
                                    if output_info is not None:
                                        previous_final_output.append(output_info[str(command_id)]['final_output'])
                                        self.action_log['result']['outputs'][key_list_command]['config'].append(
                                            output_info)
                                        stringhelpers.info("\nAction: [%s]-- config step [%s]: filnal-output: %s" % (
                                        self.action_id, step, str(output_info[str(command_id)]['final_output'])))
                                        if int(step) > 1:
                                            if int(output_info[str(command_id)]['final_output']) == int(
                                                    _command_running.get('condition', 0)):
                                                compare_final_output.append(True)
                                            else:
                                                self.action_log['final_output'] = False
                                                compare_final_output = []
                                                break
                                    else:
                                        previous_final_output.append(False)
                                        if int(step) > 1:
                                            self.action_log['final_output'] = False
                                            compare_final_output = []
                                            break
                            else:
                                output_info = self.process_each_command(command_id, _command_running)
                                if output_info is not None:
                                    previous_final_output.append(output_info[str(command_id)]['final_output'])
                                    self.action_log['result']['outputs'][key_list_command]['config'].append(output_info)
                                    stringhelpers.info("\nAction: [%s]-- config step [%s]: filnal-output: %s" % (self.action_id, step, str(output_info[str(command_id)]['final_output'])))
                                    if int(step) > 1:
                                        if int(output_info[str(command_id)]['final_output']) == int(_command_running.get('condition', 0)):
                                            compare_final_output.append(True)
                                        else:
                                            self.action_log['final_output'] = False
                                            compare_final_output = []
                                            break
                                else:
                                    previous_final_output.append(False)
                                    if int(step) > 1:
                                        self.action_log['final_output'] = False
                                        compare_final_output=[]
                                        break
                    else:  # last command in actions check point
                        try:
                            dependency = int(_command_running['dependency'])
                            if dependency > 0 and int(step) > 0:
                                continue
                            if (int(_command_running['condition']) == int(previous_final_output[dependency - 1])):
                                compare_final_output.append(True)
                            else:
                                compare_final_output.append(False)
                        except:
                            compare_final_output.append(False)

                # -------------- compare final_output for action ----------------------------------------------------
                try:
                    if len(compare_final_output) > 0:
                        first_value = None
                        count = 0
                        for x in compare_final_output:
                            if count == 0:
                                first_value = x
                            else:
                                first_value = func_compare('=', first_value, x)
                            count = count + 1

                        self.action_log['final_output'] = first_value
                        self.final_result = first_value #final result run action
                        self.dict_state_result['final_result_action'] = self.final_result
                    else:
                        if len(previous_final_output) > 0:
                            for x in previous_final_output:
                                self.dict_state_result['final_result_action'] = x
                        else:
                            self.dict_state_result['final_result_action'] = False


                    self.dict_state_result['action_log'] = self.action_log

                except Exception as ex:
                    stringhelpers.err("MEGA ACTIONS THREAD ERROR COMPARE ACTION FINAL-OUTPUT: %s | THREAD %s" % (ex, self.name))
                    # ---------------------------------------------------------------------------------------------------

            '''######################################################################################################'''

            '''#############################process command by rollback dependency###################################'''
            if len(_array_step_rollback) > 0 and self.is_rollback ==True:
                compare_final_output = []
                previous_final_output = []
                for step in _array_step_rollback:

                    if action_type == 'Get':
                        self.dict_state_result['final_result_action'] = True
                        break

                    _command_running = _dict_list_command_rollback[step]
                    # if _command_running['dependency'] == '0':
                    command_id = _command_running.get('command_id', 0)
                    if command_id > 0:  # command_id > 0
                        dependency = int(_command_running['dependency'])
                        if dependency > 0:  # run need compare
                            dependStep = dependency
                            if (int(_command_running['condition']) == int(previous_final_output[dependStep - 1])):
                                command_type = _command_running.get('type', None)
                                if command_type is not None:
                                    if int(command_type) == 5:
                                        output_info = self.process_each_command(command_id, _command_running)
                                        previous_final_output.append(True)
                                    else:
                                        output_info = self.process_each_command(command_id, _command_running)
                                        if output_info is not None:
                                            previous_final_output.append(output_info[str(command_id)]['final_output'])
                                            self.action_log['result']['outputs'][key_list_command]['rollback'].append(
                                                output_info)
                                            stringhelpers.info(
                                                "\nAction: [%s]-- rollback step [%s]: filnal-output: %s" % (
                                                self.action_id, step,
                                                str(output_info[str(command_id)]['final_output'])))
                                        else:
                                            previous_final_output.append(False)
                            else:
                                stringhelpers.err(
                                    "MEGA ACTIONS ROLLBACK STEP: %s NOT AVAIABLE WITH FINAL_OUTPUT OF STEP %d| THREAD %s" % (step, dependStep, self.name))
                                previous_final_output.append(False)
                                continue
                        else:  # dependency == 0
                            command_type = _command_running.get('type', None)
                            if command_type is not None:
                                if int(command_type) == 5:
                                    output_info = self.process_each_command(command_id, _command_running)
                                    previous_final_output.append(True)
                                else:
                                    output_info = self.process_each_command(command_id, _command_running)
                                    if output_info is not None:
                                        previous_final_output.append(output_info[str(command_id)]['final_output'])

                                        self.action_log['result']['outputs'][key_list_command]['rollback'].append(output_info)

                                        stringhelpers.info("\nAction: [%s]-- rollback step [%s]: filnal-output: %s" % (
                                        self.action_id, step, str(output_info[str(command_id)]['final_output'])))

                                        if int(step) > 1:
                                            if int(output_info[str(command_id)]['final_output']) == int(
                                                    _command_running.get('condition', 0)):
                                                compare_final_output.append(True)
                                            else:
                                                self.action_log['final_output'] = False
                                                compare_final_output = []
                                                break
                                    else:
                                        previous_final_output.append(False)
                                        if int(step) > 1:
                                            self.action_log['final_output'] = False
                                            compare_final_output = []
                                            break
                    else:  # last command in actions check point
                        try:
                            dependency = int(_command_running['dependency'])
                            if dependency > 0 and int(step) > 0:
                                continue
                            if (int(_command_running['condition']) == int(previous_final_output[dependency - 1])):
                                compare_final_output.append(True)
                            else:
                                compare_final_output.append(False)
                        except:
                            compare_final_output.append(False)

                stringhelpers.err("MEGA ACTIONS THREAD ROLLBACK FINISHED: | THREAD %s" % (self.name))

                # -------------- compare final_output for action ----------------------------------------------------
                if action_type != 'Get':
                    try:
                        if len(compare_final_output) > 0:
                            first_value = None
                            count = 0
                            for x in compare_final_output:
                                if count == 0:
                                    first_value = x
                                else:
                                    first_value = func_compare('=', first_value, x)
                                count = count + 1

                            self.action_log['final_output'] = first_value
                            self.final_result = first_value
                            #self.dict_state_result['final_result_action_rollback'] = self.final_result
                            self.dict_state_result['final_result_action'] = self.final_result
                        else:
                            #pass
                            if len(previous_final_output) > 0:
                                for x in previous_final_output:
                                    self.dict_state_result['final_result_action'] = x
                            else:
                                self.dict_state_result['final_result_action'] = False

                        self.dict_state_result['action_rollback_log'] = self.action_log
                    except Exception as ex:
                        stringhelpers.err("MEGA ACTIONS THREAD ERROR ROLLBACK COMAPRE ACTION FINAL-OUTPUT: %s | THREAD %s" % (ex, self.name))
                        # ---------------------------------------------------------------------------------------------------

            '''##################################################################################################'''



        except Exception as e:
            stringhelpers.err("MEGA ACTIONS THREAD ERROR %s | THREAD %s" % (e, self.name))
        except ConnectionError as errConn:
            stringhelpers.err("MEGA ACTIONS CONNECT API URL ERROR %s | THREAD %s" % (self._request.url, self.name))


    def process_each_command(self, command_id = 0, _command_list = None):
        '''process command contains params'''
        try:
            self.data_command = _command_list
            command = None
            try:
                if int(self.data_command['type']) == 5:
                    sleep(int(self.data_command['delay']))
                    stringhelpers.info("\n[DELAY COMMAND %s %s]" % (command_id, self.data_command['delay']))
                    return None
            except Exception as ex_error:
                errror = ex_error

            ################### process args for command ##############################################
            command = self.data_command['command']
            ###########################################################################################

            if command is not None:
                commands = [command]
                self.fang.execute_template_action_command(commands, blanks=2, error_reporting=True, timeout=-1, terminal=False)
                result_fang = self.fang.get_action_output(self.log_output_file_name)
                # processing parsing command follow output ###########################################
                command_type = self.data_command['type']
                action_command_log = self.parsing(command_type, command_id ,result_fang, commands[0])
                return action_command_log
                ######################################################################################
            else:
                return None
        except Exception as e:
            stringhelpers.err("MEGA ACTION PROCESS EACH COMMAND ERROR %s | THREAD %s" % (e, self.name))
            return None
        except ConnectionError as errConn:
            stringhelpers.err("MEGA ACTION CONNECT API URL ERROR %s | THREAD %s" % (errConn, self.name))
            return None


    def parsing(self, command_type = 0, command_id = 0, result_fang = None, command_text = None):
        final_result_output = []
        output_result = dict()
        key = str(command_id)
        output_result[key] = dict()
        output_result[key]['output'] = []
        try:
            if command_type == 3: # alway using for ironman
                data_command_output = None
                if isinstance(self.data_command['output'], str):
                    data_command_output = json.loads(self.data_command['output'])
                else:
                    data_command_output = self.data_command['output']
                for output_item in data_command_output:
                    start_by = output_item['start_by']
                    end_by = output_item['end_by']
                    if start_by == '' and end_by == '':

                        result = {'value': '0','compare': True}
                        output_result['console_log'] = result_fang
                        output_result['command_type'] = str(command_type)
                        output_result['command_text'] = command_text
                        output_result['command_id'] =  str(command_id)

                        output_result[key]['output'].append(result)

                        #output_result[key]['console_log'] = result_fang
                        output_result[key]['final_output'] = True
                    else:
                        if end_by == 'end_row':
                            end_by = '\r\n'
                        _ret_value = stringhelpers.find_between(result_fang, start_by, end_by).strip()

                        result = {'value': '0', 'compare': True}
                        output_result['console_log'] = result_fang
                        output_result['command_type'] = str(command_type)
                        output_result['command_text'] = command_text
                        output_result['command_id'] = str(command_id)


                        output_result[key]['output'].append(result)
                        #output_result[key]['console_log'] = result_fang
                        output_result[key]['final_output'] = True
                return output_result
            elif command_type == 2 or command_type == 1:
                if isinstance(self.data_command['output'], str):
                    data_command_output = json.loads(self.data_command['output'])
                else:
                    data_command_output = self.data_command['output']
                for output_item in data_command_output:
                    #if output_item['start_by'] is not '' and output_item['end_by'] is not '':
                    try:
                        start_by = output_item['start_by']
                        end_by = output_item['end_by']
                        standard_value = output_item['standard_value']
                        compare = output_item['compare']
                        if end_by == 'end_row':
                            end_by = '\r\n'
                        compare_value = stringhelpers.find_between(result_fang, start_by, end_by)
                        if ((compare_value is not None) and (compare_value is not "")):
                            compare_value = compare_value.strip()
                        if compare_value is '' or compare_value is None:
                            compare_value = result_fang
                        #if compare_value is not None or compare_value is not '':
                        if compare != "contains":
                            compare_value = int(compare_value)
                            standard_value = int(standard_value)
                        retvalue_compare = func_compare(compare, standard_value, compare_value)
                        if compare_value == '':
                            # if compare_value empty save raw data
                            result = {'value': compare_value, 'compare': retvalue_compare, 'compare_operator': compare}
                            output_result['console_log'] = result_fang
                            output_result['command_type'] = str(command_type)
                            output_result['command_text'] = command_text
                            output_result['command_id'] = str(command_id)


                        else:
                            result = {'value': compare_value, 'compare': retvalue_compare, 'compare_operator': compare}
                            output_result['console_log'] = result_fang
                            output_result['command_type'] = str(command_type)
                            output_result['command_text'] = command_text
                            output_result['command_id'] = str(command_id)

                        output_result[key]['output'].append(result)
                        # save final result of each output
                        final_result_output.append(retvalue_compare)
                    except Exception as _error:
                        _strError = "MEGA ACTION PARSING COMMAND TYPE %d ERROR %s | THREAD %s" % (command_type, _error, self.name)

                        result = {'value': compare_value, 'compare': retvalue_compare, 'compare_operator': compare}
                        output_result['console_log'] = result_fang
                        output_result['command_type'] = str(command_type)
                        output_result['command_text'] = command_text
                        output_result['command_id'] = str(command_id)


                        output_result[key]['output'].append(result)
                        output_result[key]['parsing_status'] = 'ERROR'
                        stringhelpers.err(_strError)
                        final_result_output.append(False)


                # determine operator for final output
                try:
                    final_operator = []
                    for x in self.data_command['final_output']:
                        if x == '&' or x == '|':
                            final_operator.append(x)
                        else:
                            pass

                    # compare final output
                    number_operator = 0
                    first_value = None
                    for x in final_result_output:
                        if len(final_operator) > 0:
                            if number_operator == 0:
                                first_value = x
                            else:
                                first_value = func_compare(final_operator[number_operator - 1], first_value, x)
                            number_operator = number_operator + 1

                            if number_operator == len(final_result_output):
                                output_result[key]['final_output'] = first_value
                        else:
                            output_result[key]['final_output'] = x
                except Exception as _errorFinal:
                    if len(final_result_output) > 0:
                        output_result[key]['final_output'] = final_result_output[0]
                    _strError = "\nMEGA ACTION CALCULATOR FINAL_OUTPUT  COMMAND_TYPE %d ERROR %s | THREAD %s" % (command_type, _errorFinal, self.name)
                    stringhelpers.err(_strError)



                return output_result
        except Exception as _errorException:
            output_result[key]['parsing_status'] = 'ERROR'
            _strError = "MEGA ACTION PARSING COMMAND TYPE %d ERROR %s | THREAD %s" % (command_type, _errorException, self.name)
            stringhelpers.err(_strError)
            return  output_result

    def join(self):
        threading.Thread.join(self)
        return self.dict_state_result

''' -----------------------------------------------------------------------------------------------------------------'''
