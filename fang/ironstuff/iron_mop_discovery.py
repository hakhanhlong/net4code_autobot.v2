import threading
from ultils import stringhelpers
from api.request_helpers import RequestHelpers
from api.request_url import RequestURL
from network_adapter.factory_connector import FactoryConnector
from . import func_compare

from database.impl.networkobject_impl import NetworkObjectImpl
from datetime import datetime
from time import time, sleep

import json



#@functools.total_ordering
class Iron_Mop_Discovery(threading.Thread):
    """ Thread instance each process template """
    def __init__(self,  name, sub_mop = None, dict_template = {}, mop_id = None, table_name=None, output_mapping=None,
                 key_merge=None, submop_index=None, dict_version_container = None, len_submops = None,
                 socketio=None,
                 socketio_iron=None):
        threading.Thread.__init__(self)
        self.name = name
        self.sub_mop = sub_mop
        self.dict_template = dict_template
        self.requestURL = RequestURL()
        self._request = RequestHelpers()

        self.info_fang = self.buildinfo_subtemplates()
        self.result_templates = []
        self.done = False

        self.mop_id = mop_id
        self.start_time = time()
        self.table_name = table_name
        self.output_mapping = output_mapping
        self.key_merge = key_merge
        self.submop_index = submop_index
        self.is_started  = False
        self.dict_version_container = dict_version_container
        self.len_submops = len_submops

        self.socketio = socketio
        self.socketio_iron = socketio_iron



    def update_mop_status(self, status, duration=None):
        # ---------------update mega_status to action------------------------------------------------
        self._request.url = self.requestURL.IRONMAN_URL_MOP_UPDATE % (self.mop_id)
        #dict_update = {'iron_status': status}
        dict_update = {'flash_status': status}
        if status == 'running':
            dict_update['start_time'] = datetime.now().strftime("%Y-%m-%d %H:%M")
        if status == 'done' or status == 'rolledback':
            #key_template = 'template_%d' % (self.mop_id)
            #del self.dict_template[key_template]
            dict_update['end_time'] = datetime.now().strftime("%Y-%m-%d %H:%M")
            dict_update['duration_time'] = '%.2f' % (duration - self.start_time)

        self._request.params = dict_update
        self._request.put()

    def run(self):
        self.is_started = True
        if self.info_fang is not None:
            #-----------------------------------------------------------------------------------------------------------
            count = 0
            for fang in self.info_fang['subtemplates']: # fang sub template
                sub_template_name = fang['sub_template_name']
                #out_mapping = self.output_mapping.get(str(count), None)
                subtemplate_thread = SubTemplate(sub_template_name, fang, False, self.result_templates, int(fang['mode']),
                                                 self.table_name, self.output_mapping, self.key_merge, self.submop_index,
                                                 self.dict_version_container, self.mop_id, self.len_submops, self.socketio,
                                                 self.socketio_iron)
                self.update_mop_status('running')
                subtemplate_thread.start()
                dict_template = dict(sub_template_name = sub_template_name, state = subtemplate_thread.join(), fang=fang, mode=int(fang['mode']))
                self.update_mop_status('done', time())
                self.result_templates.append(dict_template)
                count = count + 1
            # ----------------------------------------------------------------------------------------------------------
        else:
            stringhelpers.warn("[%s] IRON TEMPLATE NOT DATA TO FANG\r\n" % (self.name),
                                      socket_namespace=self.socketio_iron, on_command_text='overall_terminal')

        self.done = True

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
                    if len(v['actions']) > 0: #check if actions is not empty
                        for action in v['actions']:  # list actions
                            count_step = count_step + 1  # step
                            dict_action[str(count_step)] = action
                        info_fang['actions'] = dict_action
                        subtemplate['devices'].append(info_fang)
                    else:
                        info_fang['actions'] = None
                except Exception as _error:
                    stringhelpers.err("IRON MOP DISCOVERY BUILD buildinfo_subtemplates ERROR %s\n\r" % (_error),
                                      socket_namespace=self.socketio_iron, on_command_text='overall_terminal')
            if subtemplate is not None:
                data_fang['subtemplates'].append(subtemplate)
        except:
            pass

        return data_fang

    def join(self):
        threading.Thread.join(self)
        return self.done





class SubTemplate(threading.Thread):
    '''sub template'''
    def __init__(self, name, subtemplate=None, is_rollback=False, result_templates = None, mode = 0, table_name=None,
                 output_mapping=None, key_merge=None, submop_index=None, dict_version_container=None, mop_id=None,
                 len_submops=None, socketio=None, socketio_iron=None):
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
        self.table_name = table_name
        self.output_mapping = output_mapping
        self.key_merge = key_merge
        self.submop_index = submop_index
        self.dict_version_container = dict_version_container
        self.mop_id = mop_id
        self.len_submops = len_submops

        self.socketio = socketio
        self.socketio_iron = socketio_iron




    def excecute(self, data_fang):

        actions = data_fang.get('actions', None)
        if actions is None:
            stringhelpers.info('\n[IRON][DISCOVERY][ACTIONS IS NONE] %s' % (str(self.name)),
                                      socket_namespace=self.socketio_iron, on_command_text='overall_terminal')
            return None



        actions = sorted(data_fang['actions'].items(), reverse=False)  # get actions of each sub template # action contain linkedlist
        #--------------------- build info device fang ------------------------------------------------------------------
        device = data_fang['device']['device_info']
        self.dict_state_result[str(device['device_id'])] = {}
        vendor_ios = data_fang['device']['vendor_ios']
        #vendor_ios = data_fang['device']['vendor'] + '|' + data_fang['device']['os']
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
            'timeout': 10,
            'socketio': self.socketio,
            'socket_namespace': self.socketio_iron,
            'socket_command': 'overall_terminal',
            'device_id': int(device['device_id'])
        }
        stringhelpers.info("\nIRON DISCOVERY FANG DEVICE: host=%s, port=%s, devicetype=%s \n" % (parameters['host'], parameters['port'], parameters['device_type']),
                                      socket_namespace=self.socketio_iron, on_command_text='overall_terminal')
        fac = FactoryConnector(**parameters)
        log_output_file_name = "%s.log" % (stringhelpers.generate_random_keystring(10))
        fac = fac.execute_keep_alive(loginfo=log_output_file_name)
        if not fac.is_alive():
            stringhelpers.info("CONNECT DEVICE: host=%s, port=%s, devicetype=%s FAIL\n\n" % (parameters['host'], parameters['port'], parameters['device_type']),
                                      socket_namespace=self.socketio_iron, on_command_text='overall_terminal')
            fac = fac.execute_keep_alive(loginfo=log_output_file_name)
            stringhelpers.info("CONNECT DEVICE: host=%s, port=%s, devicetype=%s RE-CONNECTING\n\n" % (
            parameters['host'], parameters['port'], parameters['device_type']),
                                      socket_namespace=self.socketio_iron, on_command_text='overall_terminal')
            if not fac.is_alive():
                return None
        else:
            self.socketio_iron.emit('on_current_device', {'mop_id':self.mop_id, 'submop':self.submop_index, 'device_id':int(device['device_id'])})
            stringhelpers.info_green("\nIRON DISCOVERY CONNECTED DEVICE [SUCCESS]: host=%s, port=%s, devicetype=%s \n" % (parameters['host'], parameters['port'], parameters['device_type']),
                                      socket_namespace=self.socketio_iron, on_command_text='overall_terminal')
        #---------------------------------------------------------------------------------------------------------------

        # --------------- list dict action command ---------------------------------------------------------------------
        _dict_list_actions = dict()
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


            #if str(device['device_id']) == '2017' and self.submop_index == 3:
            #    test = "longhk"


            for step  in _array_step:
                # print(_dict_list_actions[step])
                _action = _dict_list_actions[str(step)]
                action_id = int(_action.get('action_id', 0))

                if action_id > 0:  # command_id > 0
                    try:
                        data_fields = self.output_mapping[str(action_id)][vendor_ios]
                    except Exception as _error_data_fields:
                        self.array_state_action = []
                        fac.remove_file_log(log_output_file_name)
                        fac.terminal()  # finished fang command

                        stringhelpers.err('[ERROR][DO NOT VENDOR_IOS] %s DEVICE ID: %s ACTION ID: %s' % (
                        vendor_ios, str(device['device_id']), str(action_id)),
                                      socket_namespace=self.socketio_iron, on_command_text='overall_terminal')

                        return None
                    try:
                        thread_action_name = "Thread-Action_%s-In-%s" % (action_id, self.name)
                        action_data = _action

                        thread_action = Action(thread_action_name, action_data, action_id, None,
                                               None, vendor_ios,
                                               fac, self.is_rollback, log_output_file_name,
                                               deviceid=device['device_id'], table_name=self.table_name,
                                               data_fields=data_fields,
                                               key_merge=self.key_merge,
                                               submop_index=self.submop_index,
                                               dict_version_container=self.dict_version_container,
                                               mop_id=self.mop_id, len_submops=self.len_submops,
                                               socketio=self.socketio, socketio_iron=self.socketio_iron)
                        thread_action.start()
                        result = thread_action.join()
                        result['action_id'] = action_id

                        result['device_id'] = device['device_id']
                        result['device_vendor_ios'] = vendor_ios

                        previous_final_output.append(True)

                        self.array_state_action.append(result)

                    except:
                        stringhelpers.warn("[%s] IRON TEMPLATE REQUEST DATA ACTION %s FAIL\r\n" % (self.name, action_id),
                                      socket_namespace=self.socketio_iron, on_command_text='overall_terminal')
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





    def run(self):
        try:
            if self.subtemplate is not None:
                threading_array = []
                stringhelpers.info("\n[INFO]-RUN SUBTEMPLATE: %s" % (self.name),
                                      socket_namespace=self.socketio_iron, on_command_text='overall_terminal')
                filnal_result = []

                #------------------ chay ko song song ------------------------------------------------------------------

                if self.mode == 1: #mode = 1, not parallel

                    for device in self.subtemplate['devices']:
                        device_id = device['device']['device_info']['device_id']

                        # -------------- check has run next subtemplate belong previous result subtemplate
                        if len(self.result_templates) > 0:
                            before_result = self.result_templates[len(self.result_templates) - 1]
                            try:
                                final_sub_template = before_result['state'][str(device_id)]['final_sub_template']
                                if final_sub_template == False:
                                    stringhelpers.info_green("SUB TEMPLATE: %s FOR DEVICE: %s DON'T CONTINIOUS RUN\n\n" % (
                                        self.name, device_id),
                                      socket_namespace=self.socketio_iron, on_command_text='overall_terminal')
                                    break
                            except:
                                stringhelpers.err(
                                    "SUB TEMPLATE: %s FOR DEVICE: %s DON'T CONTINIOUS RUN\n\n" % (self.name, device_id),
                                      socket_namespace=self.socketio_iron, on_command_text='overall_terminal')
                                break

                        # ------------------------------------------------------------------------------------------
                        if len(filnal_result) == 0:
                            self.excecute(device)
                        else:
                            if filnal_result[len(filnal_result) - 1] == True:
                                self.excecute(device)

                        try:
                            filnal_result.append(
                                self.dict_state_result[str(device_id)]["final_sub_template"])
                        except:
                            pass


                    #---------------------------------------------------------------------------------------------------
                else: # mode = 2, run parallel

                    #------------------- chay song song ----------------------------------------------------------------
                    for device in self.subtemplate['devices']:
                        device_id = device['device']['device_info']['device_id']
                        # -------------- check has run next subtemplate belong previous result subtemplate
                        if len(self.result_templates) > 0:
                            before_result = self.result_templates[len(self.result_templates) - 1]
                            try:
                                final_sub_template = before_result['state'][str(device_id)]['final_sub_template']
                                if final_sub_template == False:
                                    stringhelpers.err("SUB TEMPLATE: %s FOR DEVICE: %s DON'T CONTINIOUS RUN\n\n" % (
                                    self.name, device_id),
                                      socket_namespace=self.socketio_iron, on_command_text='overall_terminal')
                                    break
                            except:
                                stringhelpers.err(
                                    "SUB TEMPLATE: %s FOR DEVICE: %s DON'T CONTINIOUS RUN\n\n" % (self.name, device_id),
                                      socket_namespace=self.socketio_iron, on_command_text='overall_terminal')
                                break

                        # ------------------------------------------------------------------------------------------
                        if len(filnal_result) == 0:
                            _thread = threading.Thread(target=self.excecute, args=(device,))
                            _thread.start()
                            sleep(0.3)
                            threading_array.append(_thread)
                        else:
                            if filnal_result[len(filnal_result) - 1] == True:
                                _thread = threading.Thread(target=self.excecute, args=(device,))
                                _thread.start()
                                sleep(0.3)
                                threading_array.append(_thread)

                    for x in threading_array:
                        sleep(0.3)
                        x.join()
                    threading_array = []

                    for device in self.subtemplate['devices']:
                        device_id = device['device']['device_info']['device_id']
                        try:
                            filnal_result.append(self.dict_state_result[str(device_id)]["final_sub_template"])
                        except:
                            pass
                    #-------------------------------------------------------------------------------------------------------
        except Exception as exError:
            stringhelpers.err("[ERROR] RUN SUBTEMPLATE-[%s]: %s" % (self.name, exError),
                                      socket_namespace=self.socketio_iron, on_command_text='overall_terminal')

    def join(self):
        threading.Thread.join(self)
        return self.dict_state_result


''' --------------------------------- Action ------------------------------------------------------------------------'''
class Action(threading.Thread):
    """ Thread instance each process mega """
    def __init__(self, name, data_action = None, action_id = None, params_action=None, param_rollback_action=None,
                 vendor_os=None, session_fang=None, is_rolback=False, file_log=None,
                 deviceid=None, table_name=None, data_fields=None, key_merge=None, submop_index=None,
                 dict_version_container=None, mop_id=None, len_submops=None, socketio=None, socketio_iron=None):
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

        self.submop_index = submop_index

        self.params_action = params_action
        self.param_rollback_action = param_rollback_action

        self.is_rollback = is_rolback

        self.final_result = False
        self.dict_state_result = dict()
        self.deviceid = deviceid



        self.table_name = table_name
        self.data_fields = data_fields
        self.key_merge = key_merge
        self.dict_version_container = dict_version_container
        self.mop_id = mop_id
        self.len_submops=len_submops

        self.socketio = socketio
        self.socketio_iron = socketio_iron


    def send_command_log_sockbot(self, data_send):
        self.socketio_iron.emit('on_device_terminal', data_send)

    def run(self):
        try:
            key_list_command = self.vendor_os
            self.action_log['result']['outputs'][key_list_command] = {}
            self.action_log['result']['outputs'][key_list_command]['config'] = []
            self.action_log['result']['outputs'][key_list_command]['rollback'] = []

            action_type = self.data_action.get('category_1', None)  # thieeu category_1 tra ra tu json
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
                                command_type = int(_command_running.get('type', None))
                                if command_type is not None:
                                    if command_type == 5:  # process delay command
                                        output_info = self.process_each_command(command_id, _command_running, step)
                                        previous_final_output.append(True)
                                    else:
                                        output_info = self.process_each_command(command_id, _command_running, step)
                                        if output_info is not None:
                                            previous_final_output.append(output_info[str(command_id)]['final_output'])
                                            self.action_log['result']['outputs'][key_list_command]['config'].append(
                                                output_info)
                                            stringhelpers.info(
                                                "\nAction: [%s]-- config step [%s]: filnal-output: %s" % (
                                                self.action_id, step,
                                                str(output_info[str(command_id)]['final_output'])),
                                                socket_namespace=self.socketio_iron, on_command_text='overall_terminal')
                                        else:
                                            # previous_final_output.append(False)
                                            previous_final_output.append(True)
                            else:
                                _msg = "IRON ACTIONS STEP: %s NOT AVAIABLE WITH FINAL_OUTPUT OF STEP %d| THREAD %s" % (step, dependStep, self.name)
                                stringhelpers.err(_msg, socket_namespace=self.socketio_iron, on_command_text='overall_terminal')
                                #self.send_command_log_sockbot({'device_id': self.deviceid, 'arr_data_text': [_msg]})
                                previous_final_output.append(False)
                                continue
                        else:  # dependency == 0
                            command_type = int(_command_running.get('type', None))
                            if command_type is not None:
                                if command_type == 5:  # process delay command
                                    output_info = self.process_each_command(command_id, _command_running, step)
                                    previous_final_output.append(True)
                                else:
                                    output_info = self.process_each_command(command_id, _command_running, step)
                                    if output_info is not None:
                                        previous_final_output.append(output_info[str(command_id)]['final_output'])
                                        self.action_log['result']['outputs'][key_list_command]['config'].append(
                                            output_info)
                                        _msg = "\nAction: [%s]-- config step [%s]: filnal-output: %s" % (
                                        self.action_id, step, str(output_info[str(command_id)]['final_output']))
                                        stringhelpers.info(_msg, socket_namespace=self.socketio_iron, on_command_text='overall_terminal')
                                        #self.send_command_log_sockbot({'device_id': self.deviceid, 'arr_data_text': [_msg]})

                                        if int(step) > 1:
                                            if int(output_info[str(command_id)]['final_output']) == int(
                                                    _command_running.get('condition', 0)):
                                                compare_final_output.append(True)
                                            else:
                                                # self.action_log['final_output'] = False
                                                self.action_log['final_output'] = True
                                                compare_final_output = []
                                                break
                                    else:
                                        # previous_final_output.append(False)
                                        previous_final_output.append(True)
                                        if int(step) > 1:
                                            # self.action_log['final_output'] = False
                                            self.action_log['final_output'] = True
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
                                #compare_final_output.append(False)
                                compare_final_output.append(True)
                        except:
                            #compare_final_output.append(False)
                            compare_final_output.append(True)

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
                            #self.dict_state_result['final_result_action'] = False
                            self.dict_state_result['final_result_action'] = True

                except Exception as ex:
                    _msg = "IRON ACTIONS THREAD ERROR COMAPRE ACTION FINAL-OUTPUT: %s | THREAD %s" % (ex, self.name)
                    stringhelpers.err(_msg, socket_namespace=self.socketio_iron, on_command_text='overall_terminal')
                    #self.send_command_log_sockbot({'device_id': self.deviceid, 'arr_data_text': [_msg]})
                    # ---------------------------------------------------------------------------------------------------

            '''######################################################################################################'''

        except Exception as e:
            _msg = "IRON ACTIONS THREAD ERROR %s | THREAD %s" % (e, self.name)
            stringhelpers.err(_msg, socket_namespace=self.socketio_iron, on_command_text='overall_terminal')
            #self.send_command_log_sockbot({'device_id': self.deviceid, 'arr_data_text': [_msg]})

        except ConnectionError as errConn:
            _msg = "IRON ACTIONS CONNECT API URL ERROR %s | THREAD %s" % (self._request.url, self.name)
            stringhelpers.err(_msg, socket_namespace=self.socketio_iron, on_command_text='overall_terminal')
            #self.send_command_log_sockbot({'device_id': self.deviceid, 'arr_data_text': [_msg]})


    def process_each_command(self, command_id = 0, _command_list = None, step=''):
        '''process command contains params'''
        try:
            self.data_command = _command_list
            command = None


            #-------------------- process delay command ---------------------------------------------------
            try:
                if int(self.data_command['type']) == 5:
                    sleep(int(self.data_command['delay']))
                    _msg = "[DELAY COMMAND %s %s]" % (command_id, self.data_command['delay'])
                    stringhelpers.info(_msg, socket_namespace=self.socketio_iron, on_command_text='overall_terminal')
                    #self.send_command_log_sockbot({'device_id': self.deviceid, 'arr_data_text': [_msg]})
                    return None
            except Exception as ex_error:
                errror = ex_error
            #----------------------------------------------------------------------------------------------



            ################### process args for command ##############################################
            command = self.data_command['command']
            ###########################################################################################

            if command is not None:
                commands = [command]
                #stringhelpers.info_green(command)
                #result_fang = self.fang.get_output()



                # processing parsing command follow output ###########################################

                is_loop = self.data_action.get('is_loop', None)
                if is_loop is not None:
                    self.fang.execute_template_action_command(commands, blanks=2, error_reporting=True, timeout=-1, terminal=False)
                    result_fang = self.fang.get_action_output(self.log_output_file_name)
                    _msg = "\n[DISCOVERY] COMMAND '%s' IS LOOP '%s'| THREAD %s" % (commands[0], is_loop, self.name)
                    stringhelpers.info_green(_msg, socket_namespace=self.socketio_iron, on_command_text='overall_terminal')
                    self.send_command_log_sockbot({'device_id': self.deviceid, 'arr_data_text': [result_fang]})
                    #self.fang.send_sockbot_nonblocking()
                    if is_loop == 'false':
                        self.parsing(command_id ,result_fang, commands[0], step) #parsing merge
                    else:
                        self.parsing_loop(command_id, result_fang, commands[0], step) #parsing loop

                action_command_log = None
                return action_command_log
                ######################################################################################
            else:
                return None
        except Exception as e:
            _msg = "[DISCOVERY] IRON ACTION PROCESS EACH COMMAND ERROR %s | THREAD %s COMMAND %s" % (e, self.name, command)
            stringhelpers.err(_msg, socket_namespace=self.socketio_iron, on_command_text='overall_terminal')
            #self.send_command_log_sockbot({'device_id': self.deviceid, 'arr_data_text': [_msg]})
            #self.fang.terminal()
            return None
        except ConnectionError as errConn:
            _msg = "[DISCOVERY] IRON ACTION CONNECT API URL ERROR %s | THREAD %s" % (errConn, self.name)
            #self.send_command_log_sockbot({'device_id': self.deviceid, 'arr_data_text': [_msg]})
            stringhelpers.err(_msg, socket_namespace=self.socketio_iron, on_command_text='overall_terminal')
            return None


    def parsing_loop(self, command_id = 0, result_fang = None, commandtext=None, step=''):
        output_result = dict(deviceid=self.deviceid)
        output_result['rows'] = []
        key = str(command_id)
        output_result[key] = dict()
        output_result[key]['output'] = []
        try:



            dict_parsing_field = dict()

            key_loop_field = self.data_action.get('key_loop_field', None)
            key_loop_value = self.data_action.get('key_loop_value', None)
            is_process_insert = False

            array_result_fang = stringhelpers.text_to_arrayrow(result_fang)



            for x_command in self.data_command['output']:

                start_line = x_command.get('start_line', None)
                end_line = x_command.get('end_line', None)

                start_by = x_command.get('start_by', None)
                end_by = x_command.get('end_by', None)

                if end_by == 'end_row' or end_by == '\\n':
                    end_by = '\n'

                result_fang = ''
                if start_line is not None and end_line is not None:
                    if end_line == 'end_row' or end_line == '\\n':
                        end_line = '\n'
                    for row_result in array_result_fang:
                        if start_line in row_result:
                            result_fang = row_result + end_line
                            break
                    else:
                        if result_fang is '':
                            _strError = "[DISCOVERY][LOOP][ERROR][START_LINE][ON_ROW][RESULT = NULL] " \
                                        "START_LINE = %s|MOPID:%s|DEVICE ID:%s |COMMAND ID: %s|COMMAND:%s| THREAD %s" % \
                                        (start_line, str(self.mop_id), str(self.deviceid), str(command_id),commandtext,self.name)
                            stringhelpers.err(_strError,socket_namespace=self.socketio_iron, on_command_text='overall_terminal')
                    #result_fang = stringhelpers.find_between_keep_str_start(result_fang, start_line, end_line)

                if result_fang is not '':
                    try:
                        field_name = x_command.get('name', None)
                        field_name = self.data_fields[str(command_id)].get(field_name, None)
                        if field_name is None:
                            field_name = field_name.lower()
                            field_name = self.data_fields[str(command_id)].get(field_name, None)
                    except Exception as _error_field:
                        _strError = "[DISCOVERY][LOOP][ERROR][FIELD] IRON ACTION PARSING %s ERROR %s | THREAD %s" % (_error_field, self.name)
                        stringhelpers.err(_strError,socket_namespace=self.socketio_iron, on_command_text='overall_terminal')

                    filter_result_fang = stringhelpers.find_between(result_fang, start_by, end_by)

                    if filter_result_fang is not None and filter_result_fang is not '':
                        dict_parsing_field[str(field_name)] = filter_result_fang
                        is_process_insert = True

            if is_process_insert:
                netwkImpl = NetworkObjectImpl()
                if self.key_merge is not None:
                    networkObj = netwkImpl.get_field_first(self.deviceid, self.table_name, key_loop_field,
                                                           key_loop_value)
                else:
                    networkObj = netwkImpl.get_field_first_loop(self.deviceid, self.table_name, key_loop_field,
                                                                key_loop_value)
                if networkObj is not None:
                    for x_field_k, x_field_v  in dict_parsing_field.items():
                        networkObj[str(x_field_k)] = x_field_v

                    if self.len_submops == self.submop_index:
                        dict_version = dict()
                        dict_db = json.loads(networkObj.to_json())
                        for k, v in dict_db.items():
                            if k not in ['_id', 'versions', 'data', 'row','column','command_id','created',
                                         'device_id', 'is_merge', 'modified', 'networkobject_id', 'row', 'table', 'versions']:
                                dict_version[str(k)] = v
                        dict_version['modifieddate'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S") #convert to json available
                        networkObj['versions'].append(dict_version)
                        stringhelpers.info('\n[VERSION][NETWORKOBJECT_ID: %s] %s' %
                                           (str(networkObj.networkobject_id), json.dumps(dict_version)),
                                           socket_namespace=self.socketio_iron, on_command_text='overall_terminal')

                    networkObj.save()
                    stringhelpers.info_green(
                        "[IRON][CALCULATE][IS_LOOP][DEVICE ID: %s, COMMAND ID: %s][INSERT FIELD %s]" % (str(self.deviceid), str(command_id), json.dumps(dict_parsing_field)), "\n",
                        socket_namespace=self.socketio_iron, on_command_text='overall_terminal')
            return output_result

        except Exception as _errorException:
            _strError = "[DISCOVERY][LOOP] IRON ACTION PARSING %s ERROR %s | THREAD %s" % (_errorException, self.name)
            stringhelpers.err(_strError,socket_namespace=self.socketio_iron, on_command_text='overall_terminal')
            return output_result


    # parsing and insert/update database
    def parsing(self, command_id = 0, result_fang = None, commandtext=None, step=''):
        output_result = dict(deviceid=self.deviceid)
        output_result['rows'] = []
        key = str(command_id)
        output_result[key] = dict()
        output_result[key]['output'] = []
        array_network_id = []
        dict_index_header = dict()
        array_header_map  = {}
        try:

            if self.data_fields is None:
                return None
            step = 0

            start_line = self.data_command['output'][step].get('start_line', None)
            end_line = self.data_command['output'][step].get('end_line', None)
            if start_line is not None and end_line is not None:
                result_fang = stringhelpers.find_between_keep_str_start(result_fang, start_line, end_line)

            start_by = self.data_command['output'][step].get('start_by', None)
            end_by = self.data_command['output'][step].get('end_by', None)


            #if ((start_by is not None) or (start_by is not '')) and ((end_by is not None) or (end_by is not '')):
            result_fang = stringhelpers.find_between_r(result_fang, start_by, end_by)


            if result_fang is None or result_fang is '':
                return None


            array_row_data = stringhelpers.text_to_arrayrow(result_fang)
            array_row_data = stringhelpers.remove_duplicates(array_row_data)
            string_contain_header = self.data_command['output'][step].get('template_header', None)  # default item 0 in array
            string_table_name = self.table_name

            data_field_master = []
            if string_contain_header is not None:
                array_header = []

                arrayRow = [x for x in array_row_data if x is not None]

                list_header = []
                list_header.append(string_contain_header)

                arrayRow[:0] = list_header

                is_next = False
                row_count = 0

                field_master = dict()


                for row in arrayRow:
                    if row == '':
                        continue
                    if '#' not in row and '---------' not in row:
                        if is_next:
                            rows_dict = dict()
                            array_value = row.split()
                            data_build = dict(versions=[])
                            data_version = {}


                            #-------- get value follow colums ------------------------------------------------------
                            is_insert = False
                            index_column = 0
                            for config_output in self.data_command['output']:
                                try:
                                    #index_column = int(config_output.get('column', None))  # value index

                                    key = config_output['header_start']
                                    start, end = dict_index_header.get(key, None)
                                    value = row[start:end].strip()


                                    #field = array_header_map.get(key, None)
                                    field = self.data_fields[str(command_id)].get(config_output['name'], None)
                                    if field is None:
                                        key_field = config_output['name'].lower()
                                        field = self.data_fields[str(command_id)].get(key_field, None)

                                    #array_check_whitespace = [v for v in value if v.isspace()]
                                    if value is not '':
                                        data_build[field] = value
                                        data_version[field] = value
                                        is_insert = True
                                        if field_master.get(str(field), None) is None:
                                            field_master[str(field)] = field
                                except:
                                    pass

                            if is_insert:
                                data_field_master.append(data_build)

                            data_version['modifieddate'] = datetime.now()
                            #---------------------------------------------------------------------------------------

                            if is_insert == True:
                                index_column = index_column + 1
                                for index, name in enumerate(array_header):
                                    try:
                                        rows_dict[name] = array_value[index]
                                    except:
                                        rows_dict[name] = ''
                                data_build['device_id'] = self.deviceid
                                data_build['data'] = rows_dict
                                data_build['table'] = string_table_name
                                data_build['column'] = index_column
                                data_build['row'] = row_count
                                data_build['command_id'] = command_id
                                #------------------- process insert/update/check database tablet interfaces --------
                                try:
                                    netwImpl = NetworkObjectImpl()

                                    intf = netwImpl.get(self.deviceid, string_table_name, index_column, row_count, command_id)

                                    if intf: #exist interfaces then update

                                        versions = intf['versions']
                                        if versions is not None:
                                            data_build['versions'] = versions
                                        array_network_id.append(intf.networkobject_id)
                                        netwImpl.update(**data_build)





                                    else: #not exist then insert

                                        if self.key_merge is not None and self.submop_index == 0:
                                            data_build['is_merge'] = True
                                            #the first time version
                                            '''try:
                                                self.dict_version_container[str(self.deviceid)] = data_version
                                            except:
                                                self.dict_version_container[str(self.deviceid)] = dict()
                                                self.dict_version_container[str(self.deviceid)] = data_version'''

                                            data_build['versions'] = []

                                            intf = netwImpl.save(**data_build)
                                            array_network_id.append(intf.networkobject_id)
                                        elif self.key_merge is not None and self.submop_index > 0:

                                            merge_item_first = netwImpl.get_field_first(self.deviceid,
                                                                                        string_table_name,
                                                                                        str(self.key_merge),
                                                                                        data_build[str(self.key_merge)])
                                            dict_insert_into_merge = dict()
                                            if merge_item_first is not None:

                                                for k, v in field_master.items():
                                                    merge_item_first[str(k)] = data_build[str(k)]
                                                    dict_insert_into_merge[str(k)] = data_build[str(k)]

                                                merge_item_first.save()
                                                stringhelpers.info_green(
                                                    "[IRON][CALCULATE][MERGE][DEVICE ID: %s, COMMAND ID: %s][INSERT FIELD][%s]" % (
                                                    str(self.deviceid), str(command_id), json.dumps(dict_insert_into_merge)), "\n",
                                                    socket_namespace=self.socketio_iron,
                                                    on_command_text='overall_terminal')

                                            else:
                                                intf = netwImpl.save(**data_build)
                                                array_network_id.append(intf.networkobject_id)
                                        else:
                                            data_build['versions'].append(data_version)
                                            #insert nhu binh thuong
                                            intf = netwImpl.save(**data_build)
                                            array_network_id.append(intf.networkobject_id)


                                except Exception as ex:
                                    _strError = "[DISCOVERY][INSERT][UPDATE][%s]: %s | THREAD %s" % (ex, string_table_name, self.name)
                                    stringhelpers.err(_strError,socket_namespace=self.socketio_iron, on_command_text='overall_terminal')
                                #-------------------------------------------------------------------------------------------

                                output_result['rows'].append(rows_dict)

                        if (string_contain_header in row) or ('h1' in string_contain_header) or ('h2' in string_contain_header):
                            # build header and extract size header for value
                            for config_output in self.data_command['output']:
                                try:
                                    if is_next is not True:
                                        if ('h1' in string_contain_header) or ('h2' in string_contain_header):
                                            #header_start #header_end
                                            #process header manual definition
                                            header_start = config_output['header_start']
                                            header_end = config_output.get('header_end', None)
                                            index_start = row.index(header_start)

                                            name = config_output.get('name', None) #save field to db
                                            if header_end is None or header_end is '':
                                                index_end = len(row) * 15
                                            else:
                                                index_end = row.index(header_end)

                                            header = row[index_start:index_end].strip()

                                            array_header_map[header] = name
                                            dict_index_header[header] = (index_start, index_end)

                                            array_header.append(header)
                                        else:
                                            # header_start #header_end
                                            header_start = config_output['header_start']
                                            header_end = config_output.get('header_end', None)
                                            index_start = row.index(header_start)
                                            name = config_output.get('name', None)  # save field to db

                                            if header_end is None or header_end is '':
                                                index_end = len(row) * 15
                                            else:
                                                index_end = row.index(header_end)

                                            header = row[index_start:index_end].strip()

                                            array_header_map[header] = name
                                            dict_index_header[header] = (index_start, index_end)
                                            array_header.append(header)

                                except Exception as _outputHeaderError:
                                    _strError = "[DISCOVERY][PARSING][HEADER][%s]: %s | THREAD %s" % (self.name, _outputHeaderError)
                                    stringhelpers.err(_strError,socket_namespace=self.socketio_iron, on_command_text='overall_terminal')

                            is_next = True
                    row_count = row_count + 1

                # -------------------------------process delete interfaces & lldp if device not exist interface and lldp-----
                array_delete_networkobject = []
                if len(array_network_id) > 0:
                    netwImpl = NetworkObjectImpl()
                    list = netwImpl.get_list(self.deviceid, string_table_name, command_id)
                    if len(list) > 0:
                        for x in list:
                            if x.networkobject_id not in array_network_id:
                                array_delete_networkobject.append(x.networkobject_id)
                        if len(array_delete_networkobject) > 0:
                            for d in array_delete_networkobject:
                                netwImpl.delete(d)
                                stringhelpers.err(
                                    '[DELETE][NETWORK_OBJECT_ID] - %s [DEVICE ID]=%s [COMMAND ID] = %s' % (
                                        str(d), str(self.deviceid), str(command_id)), '\n\n',
                                    socket_namespace=self.socketio_iron, on_command_text='overall_terminal')
                # --------------------------------------------------------------------------------------------------------------

            else:
                stringhelpers.err('[HEADER NOT FOUND][COMMAND ID:%s]' % (str(command_id)), '\n\n',
                                  socket_namespace=self.socketio_iron, on_command_text='overall_terminal')

                #-----------------------------------------------------------------------------------------------------------------------------

            return output_result
        except Exception as _errorException:
            output_result[key]['parsing_status'] = 'ERROR'
            _strError = "[DISCOVERY] IRON ACTION PARSING %s ERROR %s | THREAD %s" % (_errorException, self.name)
            stringhelpers.err(_strError, socket_namespace=self.socketio_iron, on_command_text='overall_terminal')
            return  output_result

    def join(self):
        threading.Thread.join(self)
        return self.dict_state_result

''' -----------------------------------------------------------------------------------------------------------------'''

