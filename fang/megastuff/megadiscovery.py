import threading
from ultils import stringhelpers
from api.request_helpers import RequestHelpers
from api.request_url import RequestURL
from network_adapter.factory_connector import FactoryConnector
from . import func_compare
import json

from database.impl.interfaces_Impl import InterfaceImpl
from database.impl.lldp_impl import LLDPImpl




class MegaDiscovery(threading.Thread):
    """ Thread instance each process template """
    def __init__(self, name, data_template = None, dict_template = {}):
        threading.Thread.__init__(self)
        self.name = name
        self.data_template = data_template
        self.dict_template = dict_template
        self.requestURL = RequestURL()
        self._request = RequestHelpers()

        self.info_fang = self.buildinfo_subtemplates()
        self.result_templates = []

    def run(self):
        if self.info_fang is not None:
            #-----------------------------------------------------------------------------------------------------------
            for fang in self.info_fang['subtemplates']: # fang sub template
                sub_template_name = fang['sub_template_name']
                subtemplate_thread = SubTemplate(sub_template_name, fang, False, self.result_templates, int(fang['mode']))
                subtemplate_thread.start()
                dict_template = dict(sub_template_name = sub_template_name, state = subtemplate_thread.join(), fang=fang, mode=int(fang['mode']))
                self.result_templates.append(dict_template)
            # ----------------------------------------------------------------------------------------------------------


        else:
            stringhelpers.warn("[%s] MEGA TEMPLATE NOT DATA TO FANG\r\n" % (self.name))


    def buildinfo_subtemplates(self):
        data_fang = dict(subtemplates=[])
        # ----------------device list------------------------------------------------------------------------------------
        run_devices = sorted(self.data_template['run_devices'].items(), reverse=False)
        key_maps = sorted(self.data_template['map'].keys()) #key number sub template
        run_mode = self.data_template["run_mode"]

        for _k in key_maps:  # _k = number template, _v = dict role apply for sub template, sub template
            sub_template_number = _k
            subtemplate = dict(devices=[])
            dict_map_template = self.data_template['map'][sub_template_number]
            subtemplate_data = self.data_template['sub_templates'][int(sub_template_number)] #data are list action

            for k, v in run_devices:  # get list device id need fang and role of each device
                # k = deviceid, v = role of device
                device_role_name = v
                role_exist =  dict_map_template.get(device_role_name, None)
                count_step = 0
                if role_exist: # compare role of device == role of template

                    info_fang = {} #clear each add info
                    subtemplate['sub_template_name'] = self.data_template['nameMap'][sub_template_number]

                    # ------------ get data chay mode parallel ---------------------------------------------------------
                    try:
                        mode = int(run_mode.get(sub_template_number, 0))
                        if mode == 1:
                            subtemplate['mode'] = 1 # not run parallel
                        elif mode == 2:
                            subtemplate['mode'] = 2 # run parallel
                    except:
                        pass
                    # --------------------------------------------------------------------------------------------------

                    try:
                        device_fang = dict(device_id=k, role=device_role_name)
                        device_id = device_fang['device_id']

                        self._request.url = self.requestURL.URL_GET_DEVICE_DETAIL % (device_id)

                        print(self._request.url, end='\n\n')

                        device = self._request.get().json()




                        device_fang['device_info'] = dict(
                            port_mgmt=device['port_mgmt'],
                            method=device['method'],
                            vendor=device['vendor'],
                            os=device['os'],
                            username=device['username'],
                            password=device['password'],
                            ip_mgmt=device['ip_mgmt'],
                            device_id=device['device_id']
                        )
                        device_fang['vendor_ios'] = "%s|%s" % (device['vendor'], device['os'])  # vendor+os = e.x: Cisco|ios-xr
                        info_fang['device'] = device_fang

                        dict_action = dict(args=[], rollback_args=[])
                        #-----------------action in each template ----------------------------------------------------------
                        for action in subtemplate_data:  # list actions
                            count_step = count_step + 1  # step
                            dict_action[str(count_step)] = action
                            # process argument for action ------------------------------------------------------------------
                            try:
                                dict_argument = self.data_template['run_args'].get(sub_template_number, None)  # level get by number template
                                if dict_argument is not None:
                                    dict_argument = dict_argument.get(device_id, None)  # level get by deviceid
                                    if dict_argument is not None:
                                        dict_action['args'].append(dict_argument)
                            except:
                                pass
                            # -------------------------------------------------------------------------------------------
                            #ll_actions.append(dict_action)  # can xem lai co nen dung double linked list ko
                        info_fang['actions'] = dict_action
                        subtemplate['devices'].append(info_fang)
                    except Exception as _error:
                        stringhelpers.err("MEGA TEMPLATE BUILD buildinfo_subtemplates ERROR %s\n\r" % (_error))
            if subtemplate is not None:
                data_fang['subtemplates'].append(subtemplate)


        return data_fang




class SubTemplate(threading.Thread):
    '''sub template'''
    def __init__(self, name, subtemplate=None, is_rollback=False, result_templates = None, mode = 0):
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
        print("\nMEGA SUBTEMPLATE FANG DEVICE: host=%s, port=%s, devicetype=%s \n" % (parameters['host'], parameters['port'], parameters['device_type']))
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
        param_action = None
        param_rollback_action = None
        if len(actions) > 0:
            for step, action in actions:
                if str(step) != 'args' and (step) != 'rollback_args':
                    _dict_list_actions[str(step)] = action
                    _array_step.append(str(step))  # save step action
                else:
                    if str(step) == 'args': #array contain dict argument
                        param_action = action
                    else:
                        pass
        else:
            pass
        # --------------------------------------------------------------------------------------------------------------
        if len(_array_step) > 0:# and self.is_rollback == False:
            compare_final_output = []
            previous_final_output = []

            for step  in _array_step:
                # print(_dict_list_actions[step])
                _action = _dict_list_actions[str(step)]
                action_id = _action.get('action_id', 0)
                if action_id > 0:  # command_id > 0
                    self._request.url = self.requestURL.MEGA_URL_ACTION_DETAIL % (action_id)
                    try:
                        thread_action_name = "Thread-Action_%s-In-%s" % (action_id, self.name)
                        action_data = self._request.get().json()
                        dependency = int(_action['dependency'])
                        if dependency > 0:  # run need compare
                            dependStep = dependency
                            if (int(_action['condition']) == int(previous_final_output[dependStep - 1])):

                                thread_action = Action(thread_action_name, action_data, action_id, param_action,
                                                       param_rollback_action, vendor_ios,
                                                       fac, self.is_rollback,
                                                       log_output_file_name, deviceid=device['device_id'])
                                thread_action.start()
                                result = thread_action.join()
                                result['action_id'] = action_id
                                result['device_id'] = device['device_id']
                                result['device_vendor_ios'] = vendor_ios
                                previous_final_output.append(result['final_result_action'])
                                self.array_state_action.append(result)
                            else:
                                stringhelpers.err(
                                    "MEGA ACTIONS STEP: %s NOT AVAIABLE WITH FINAL_OUTPUT OF STEP %d| THREAD %s" % (
                                    step, dependStep, self.name))
                                previous_final_output.append(False)
                                continue
                        else:  # dependency == 0
                            thread_action = Action(thread_action_name, action_data, action_id, param_action,
                                                   param_rollback_action, vendor_ios,
                                                   fac, self.is_rollback, log_output_file_name,
                                                   deviceid=device['device_id'])
                            thread_action.start()
                            result = thread_action.join()
                            result['action_id'] = action_id

                            result['device_id'] = device['device_id']
                            result['device_vendor_ios'] = vendor_ios

                            previous_final_output.append(result['final_result_action'])

                            self.array_state_action.append(result)

                            if int(step) > 1:
                                if int(result['final_result_action']) == int(_action.get('condition', 0)):
                                    self.dict_state_result[str(device['device_id'])]["final_sub_template"] = True
                                else:
                                    self.dict_state_result[str(device['device_id'])]["final_sub_template"] = False
                                    compare_final_output = []
                                    break
                    except:
                        stringhelpers.warn("[%s] MEGA TEMPLATE REQUEST DATA ACTION %s FAIL\r\n" % (self.name, action_id))
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
                stringhelpers.info("\n[INFO]-RUN SUBTEMPLATE: %s" % (self.name))
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
                                    print("SUB TEMPLATE: %s FOR DEVICE: %s DON'T CONTINIOUS RUN\n\n" % (
                                    self.name, device_id))
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

                    for x in threading_array:
                        x.join()

                    for device in self.subtemplate['devices']:
                        device_id = device['device']['device_info']['device_id']
                        try:
                            filnal_result.append(self.dict_state_result[str(device_id)]["final_sub_template"])
                        except:
                            pass
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
                 vendor_os=None, session_fang=None, is_rolback=False, file_log=None,
                 deviceid=None):
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
        self.deviceid = deviceid



        # sao the nay
    def run(self):
        try:
            key_list_command = self.vendor_os
            key_rollback = 'rollback'

            self.action_log['result']['outputs'][key_list_command] = {}
            self.action_log['result']['outputs'][key_list_command]['config'] = []
            self.action_log['result']['outputs'][key_list_command]['rollback'] = []

            action_type = self.data_action['category_1']
            _list_action_commands = self.data_action['commands'][key_list_command]['config']  # list action_command config
            _list_action_rollback = self.data_action['commands'][key_list_command]['rollback']  # list action_command rollback




            # --------------- list dict action command -----------------------------------------------------------------
            _dict_list_command = dict()
            _dict_list_params = self.params_action
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
            _dict_list_params_rollback = self.param_rollback_action
            _array_step_rollback = []
            if len(_list_action_rollback) > 0:
                count = 0
                for _command in _list_action_rollback:
                    count = count + 1
                    _dict_list_command_rollback[str(count)] = _command
                    _array_step_rollback.append(str(count))  # save step command rollback
            else:
                pass
                # ------------------------------------------------------------------------------------------------------

            '''#############################process command by dependency############################################'''
            if len(_array_step) > 0 and self.is_rollback == False:
                compare_final_output = []
                previous_final_output = []
                for step in _array_step:
                    _command_running = _dict_list_command[step]
                    # if _command_running['dependency'] == '0':
                    command_id = _command_running.get('command_id', 0)
                    if command_id > 0:  # command_id > 0
                        dependency = int(_command_running['dependency'])
                        if dependency > 0:  # run need compare
                            dependStep = dependency
                            if (int(_command_running['condition']) == int(previous_final_output[dependStep - 1])):

                                output_info = self.process_each_command(command_id, _dict_list_params)
                                if output_info is not None:
                                    previous_final_output.append(output_info[str(command_id)]['final_output'])
                                    self.action_log['result']['outputs'][key_list_command]['config'].append(output_info)
                                    stringhelpers.info("\nAction: [%s]-- config step [%s]: filnal-output: %s" % (self.action_id, step, str(output_info[str(command_id)]['final_output'])))
                                else:
                                    #previous_final_output.append(False)
                                    previous_final_output.append(True)
                            else:
                                stringhelpers.err(
                                    "MEGA ACTIONS STEP: %s NOT AVAIABLE WITH FINAL_OUTPUT OF STEP %d| THREAD %s" % (step, dependStep, self.name))
                                previous_final_output.append(False)
                                continue
                        else:  # dependency == 0
                            output_info = self.process_each_command(command_id, _dict_list_params)
                            if output_info is not None:
                                previous_final_output.append(output_info[str(command_id)]['final_output'])
                                self.action_log['result']['outputs'][key_list_command]['config'].append(output_info)
                                stringhelpers.info("\nAction: [%s]-- config step [%s]: filnal-output: %s" % (self.action_id, step, str(output_info[str(command_id)]['final_output'])))
                                if int(step) > 1:
                                    if int(output_info[str(command_id)]['final_output']) == int(_command_running.get('condition', 0)):
                                        compare_final_output.append(True)
                                    else:
                                        #self.action_log['final_output'] = False
                                        self.action_log['final_output'] = True
                                        compare_final_output = []
                                        break
                            else:
                                #previous_final_output.append(False)
                                previous_final_output.append(True)
                                if int(step) > 1:
                                    #self.action_log['final_output'] = False
                                    self.action_log['final_output'] = True
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
                    stringhelpers.err("MEGA ACTIONS THREAD ERROR COMAPRE ACTION FINAL-OUTPUT: %s | THREAD %s" % (ex, self.name))
                    # ---------------------------------------------------------------------------------------------------

            '''######################################################################################################'''





        except Exception as e:
            stringhelpers.err("MEGA ACTIONS THREAD ERROR %s | THREAD %s" % (e, self.name))
        except ConnectionError as errConn:
            stringhelpers.err("MEGA ACTIONS CONNECT API URL ERROR %s | THREAD %s" % (self._request.url, self.name))


    def process_each_command(self, command_id = 0, _dict_list_params = []):
        '''process command contains params'''
        try:
            self._request.url = self.requestURL.MEGA_URL_COMMAND_DETAIL % (command_id)
            self.data_command = self._request.get().json()
            command = None

            ################### process args for command ##############################################
            #self.thread_lock.acquire()
            if len(_dict_list_params) > 0:
                for item in _dict_list_params: #array contain dict param argument
                    for k, v in item.items():
                        if command is None:
                            command = self.data_command['command']
                            command = command.replace('@{%s}' % (k), v)
                        else:
                            command = command.replace('@{%s}' % (k), v)

            else:
                command = self.data_command['command']
            #self.thread_lock.release()
            ###########################################################################################
            commands = [command]
            #stringhelpers.info_green(command)

            self.fang.execute_template_action_command(commands, blanks=2, error_reporting=True, timeout=-1, terminal=False)
            #result_fang = self.fang.get_output()
            result_fang = self.fang.get_action_output(self.log_output_file_name)


            # processing parsing command follow output ###########################################
            action_command_log = self.parsing(command_id ,result_fang, commands[0])
            action_command_log = None
            return action_command_log
            ######################################################################################
        except Exception as e:
            stringhelpers.err("[DISCOVERY] MEGA ACTION PROCESS EACH COMMAND ERROR %s | THREAD %s" % (e, self.name))
            return None
        except ConnectionError as errConn:
            stringhelpers.err("[DISCOVERY] MEGA ACTION CONNECT API URL ERROR %s | THREAD %s" % (errConn, self.name))
            return None


    def parsing(self, command_id = 0, result_fang = None, commandtext=None):
        final_result_output = []
        output_result = dict(deviceid=self.deviceid)
        output_result['rows'] = []
        key = str(command_id)
        output_result[key] = dict()
        output_result[key]['output'] = []
        array_interface_id = []
        try:

            arrayRow = stringhelpers.text_to_arrayrow(result_fang)
            if commandtext == "show interface description":
                array_header = []
                arrayRow = list(filter(None, arrayRow))
                is_next = False
                for row in arrayRow:
                    if '#' not in row:
                        if is_next:
                            rows_dict = dict()
                            array_value = row.split()
                            if len(array_value) > 0:
                                for index,name in enumerate(array_header):
                                    try:
                                        rows_dict[name] = array_value[index]
                                    except:
                                        rows_dict[name] = ''

                                #------------------- process insert/update/check database tablet interfaces ----------------
                                try:
                                    if rows_dict['Interface'] is None or rows_dict['Interface'] == '':
                                        continue
                                    interfaceimpl = InterfaceImpl()
                                    intf = interfaceimpl.get_interface(self.deviceid, rows_dict['Interface'])
                                    if intf: #exist interfaces then update
                                        interface_dict = {
                                            'device_id': self.deviceid,
                                            'interface_name': rows_dict['Interface'],
                                            'data': rows_dict
                                        }
                                        array_interface_id.append(intf.interface_id)

                                        interfaceimpl.update(**interface_dict)
                                    else: #not exist then insert
                                        interface_dict = {
                                            'device_id': self.deviceid,
                                            'interface_name': rows_dict['Interface'],
                                            'data': rows_dict
                                        }
                                        intf = interfaceimpl.save(**interface_dict)
                                        array_interface_id.append(intf.interface_id)
                                except Exception as ex:
                                    _strError = "[DISCOVERY][INSERT][UPDATE][INTERFACE]: %s | THREAD %s" % (ex, self.name)
                                    stringhelpers.err(_strError)
                                #-------------------------------------------------------------------------------------------

                                output_result['rows'].append(rows_dict)

                        if ('Interface' in row) and ('Protocol' in row): # phan loai row header
                            array_header = row.split()
                            array_header = list(filter(None, array_header))
                            is_next = True
            elif commandtext == "show lldp neighbor":
                array_process = []
                array_header = []
                arrayRow = list(filter(None, arrayRow))
                is_next = False
                for row in arrayRow:
                    if '#' not in row and 'Total entries displayed:' not in row:
                        if is_next:
                            rows_dict = dict()
                            array_value = row.split()
                            if len(array_value) > 0:
                                for index, name in enumerate(array_header):
                                    if name is not None or name is not '':
                                        try:
                                            rows_dict[name.replace(' ', '')] = array_value[index]
                                        except:
                                            rows_dict[name.replace(' ', '')] = ''

                                # ------------------- process insert/update/check database tablet interfaces ----------------
                                try:
                                    if rows_dict['DeviceID'] is None or rows_dict['LocalIntf'] == '':
                                        continue

                                    interfaceimpl = InterfaceImpl()
                                    intf = interfaceimpl.get_interface(self.deviceid, rows_dict['LocalIntf'])
                                    if intf:  # exist interfaces then process lldp
                                        interface_id = intf.interface_id
                                        lldpImpl = LLDPImpl()
                                        lldp = lldpImpl.get(interface_id)
                                        lldp_dict = {
                                            "interface_id":interface_id,
                                            "remote_interface":rows_dict['PortID'],
                                            "local_interface":rows_dict['LocalIntf'],
                                            "remote_device": rows_dict['DeviceID'],
                                            "data": rows_dict
                                        }
                                        if lldp: #update lldp
                                            lldpImpl.update(**lldp_dict)
                                        else: #insert lldp
                                            lldpImpl.save(**lldp_dict)
                                except Exception as ex:
                                    _strError = "[DISCOVERY][INSERT][UPDATE][LLDP]: %s | THREAD %s" % (ex, self.name)
                                    stringhelpers.err(_strError)
                                # --------------------------------------------------------------------------------------

                                output_result['rows'].append(rows_dict)

                        if ('Device ID' in row) and ('Port ID' in row): # phan loai row header
                            array_header = row.split('  ')
                            array_header = list(filter(None, array_header))
                            is_next = True
            else:
                _strError = "[DISCOVERY] MEGA COMMAND: %s NOT SUIABLE | THREAD %s" % (commandtext, self.name)
                stringhelpers.err(_strError)

            #-------------------------------process delete interfaces & lldp if device not exist interface and lldp-----

            array_delete_interface = []
            if len(array_interface_id) > 0:
                interfaceimpl = InterfaceImpl()
                list_interfaces = interfaceimpl.get_list_interface(self.deviceid)
                if len(list_interfaces) > 0:
                    for x in list_interfaces:
                        if x.interface_id not in array_interface_id:
                            array_delete_interface.append(x.interface_id)
            # dang xu ly
            #-----------------------------------------------------------------------------------------------------------

            return output_result
        except Exception as _errorException:
            output_result[key]['parsing_status'] = 'ERROR'
            _strError = "[DISCOVERY] MEGA ACTION PARSING %d ERROR %s | THREAD %s" % (_errorException, self.name)
            stringhelpers.err(_strError)
            return  output_result

    def join(self):
        threading.Thread.join(self)
        return self.dict_state_result

''' -----------------------------------------------------------------------------------------------------------------'''

