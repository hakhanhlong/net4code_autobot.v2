import threading
from ultils import stringhelpers
from api.request_helpers import RequestHelpers
from api.request_url import RequestURL
from network_adapter.factory_connector import FactoryConnector
import json
from . import func_compare

class MegaCommand(threading.Thread):
    """ Thread instance each process mega """
    def __init__(self, name, data_command = None, dict_command = {}):
        threading.Thread.__init__(self)
        self.name = name
        self.data_command = data_command
        self.requestURL = RequestURL()
        self.dict_command = dict_command


    def run(self):
        _request = RequestHelpers()
        _request.url = self.requestURL.URL_GET_DEVICE_DETAIL % (self.data_command["test_device"])

        try:
            device = _request.get().json()
            try:
                if device['status_code'] == 500: #device not exist
                    stringhelpers.err("DEVICE ID %s NOT EXIST | THREAD %s" % (self.data_command["test_device"], self.name))
            except: #process fang test device by command
                host = device['ip_mgmt']
                port = int(device['port_mgmt'])
                username = device['username']
                password = device['password']
                device_type = device['os']
                method = device['method'] #ssh, telnet
                parameters = {
                    'device_type': device_type,
                    'host': host,
                    'protocol': method,
                    'username': username,
                    'password': password,
                    'port': port
                }

                '''process command contains params'''
                command = None
                test_args = self.data_command['test_args']
                if len(test_args) > 0:
                    command = self.data_command['command']
                    for x in self.data_command['test_args']:
                        command = command.replace('@{%s}' % (x['name']), x['value'])
                else:
                    command = self.data_command['command']
                '''####################################'''

                commands = [command]
                fac = FactoryConnector(**parameters)
                print("FANG DEVICE: host=%s, port=%s, devicetype=%s \n\n" % (host, device['port_mgmt'], device_type))
                fang = fac.execute(commands)
                result_fang = fang.get_output()
                fang.remove_file_log(fac.file_log_command) #remove file.log

                _request.url = self.requestURL.MEGA_URL_COMMANDLOG_GETBY_COMMANDID % (self.data_command['command_id'])
                command_log = _request.get().json()
                if len(command_log) > 0:
                    cmd_log = {
                        'command_id': self.data_command['command_id'],
                        'device_id': self.data_command["test_device"],
                        'console_log': result_fang,
                        'result': dict(),
                        'command': command
                    }

                    # processing parsing command follow output ###########################################
                    command_type = self.data_command['type']
                    cmd_log = self.parsing(command_type, cmd_log)
                    ######################################################################################

                    try:
                        _request.url = self.requestURL.MEGA_URL_COMMANDLOG_UPDATE % (command_log[0]['log_id'])
                        _request.params = cmd_log
                        _request.put()
                        stringhelpers.info("MEGA THREAD INFO: %s | THREAD %s" % ("UPDATE COMMAND LOG SUCCESS", self.name))

                        #---------------update mega_status to command------------------------------------------------
                        _request.url = self.requestURL.MEGA_URL_COMMAND_UPDATE % (self.data_command['command_id'])
                        _request.params = {'mega_status':'tested'}
                        _request.put()
                        key_command = 'command_%d' % (self.data_command['command_id'])
                        del self.dict_command[key_command]
                        #--------------------------------------------------------------------------------------------
                    except ConnectionError as _conErr:
                        stringhelpers.info("MEGA THREAD ERROR: %s | THREAD %s" % (_conErr, self.name))
                else:
                    cmd_log = {
                        'command_id': self.data_command['command_id'],
                        'device_id': self.data_command["test_device"],
                        'console_log': result_fang,
                        'result': dict(),
                        'command': command
                    }

                    # processing parsing command follow output ###########################################
                    command_type = self.data_command['type']
                    cmd_log = self.parsing(command_type, cmd_log)
                    ######################################################################################

                    try:
                        _request.url = self.requestURL.MEGA_URL_COMMANDLOG_CREATE
                        _request.params = cmd_log
                        _request.post()
                        stringhelpers.info("MEGA THREAD INFO: %s | THREAD %s" % ("INSERT COMMAND LOG SUCCESS", self.name))
                        # ---------------update mega_status to command------------------------------------------------
                        _request.url = self.requestURL.MEGA_URL_COMMAND_UPDATE % (self.data_command['command_id'])
                        _request.params = {'mega_status': 'tested'}
                        _request.put()
                        key_command = 'command_%d' % (self.data_command['command_id'])
                        del self.dict_command[key_command]
                        # --------------------------------------------------------------------------------------------
                    except ConnectionError as _conErr:
                        stringhelpers.info("MEGA THREAD ERROR: %s | THREAD %s" % (_conErr, self.name))


        except Exception as e:
            stringhelpers.err("MEGA THREAD ERROR %s | THREAD %s" % (e, self.name))
        except ConnectionError as errConn:
            stringhelpers.err("MEGA CONNECT API URL ERROR %s | THREAD %s" % (_request.url, self.name))





    def parsing(self, command_type = 0, cmd_log = {}):
        final_result_output = []
        try:
            if command_type == 3: # alway using for ironman
                output_result = []
                if isinstance(self.data_command['output'], str):
                    data_command_output = json.loads(self.data_command['output'])
                else:
                    data_command_output = self.data_command['output']
                for output_item in data_command_output:
                    start_by = output_item['start_by']
                    end_by = output_item['end_by']
                    if start_by == '' and end_by == '':
                        output_result.append({'value': cmd_log['console_log'], 'compare': True})
                        cmd_log['result']['outputs'] = output_result
                        cmd_log['result']['final_output'] = True
                    else:
                        if end_by == 'end_row':
                            end_by = '\r\n'
                        _ret_value = stringhelpers.find_between(cmd_log['console_log'], start_by, end_by).strip()
                        output_result.append({'value': _ret_value, 'compare': True})
                        cmd_log['result']['outputs'] = output_result
                        cmd_log['result']['final_output'] = True
                return cmd_log
            elif command_type == 2 or command_type == 1:
                output_result = []
                if isinstance(self.data_command['output'], str):
                    data_command_output = json.loads(self.data_command['output'])
                else:
                    data_command_output = self.data_command['output']
                for output_item in data_command_output:
                    if output_item['start_by'] is not '' and output_item['end_by'] is not '':
                        try:
                            start_by = output_item['start_by']
                            end_by = output_item['end_by']
                            standard_value = output_item['standard_value']
                            compare = output_item['compare']
                            if end_by == 'end_row':
                                end_by = '\r\n'
                            compare_value = stringhelpers.find_between(cmd_log['console_log'], start_by, end_by).strip()
                            if compare_value is not None or compare_value is not '':
                                if compare != "contains":
                                    compare_value = int(compare_value)
                                    standard_value = int(standard_value)
                                retvalue_compare = func_compare(compare, standard_value, compare_value)
                                output_result.append({'value': compare_value, 'compare': retvalue_compare})
                                # save final result of each output
                                final_result_output.append(retvalue_compare)
                        except Exception as _error:
                            _strError = "MEGA PARSING COMMAND TYPE %d ERROR %s | THREAD %s" % (command_type, _error, self.name)
                            stringhelpers.err(_strError)
                            output_result.append({'value': compare_value, 'compare': retvalue_compare, 'error': _strError})
                            cmd_log['parsing_status'] = 'ERROR'
                            final_result_output.append(False)


                # determine operator for final output
                count_operator = 0
                final_operator = []
                for x in self.data_command['final_output']:
                    if x == '&' or x == '|':
                        final_operator.append(x)

                # compare final output
                number_operator = 0
                first_value = None
                for x in final_result_output:
                    if number_operator == 0:
                        first_value = x
                    else:
                        first_value = func_compare(final_operator[number_operator-1], first_value, x)
                    number_operator = number_operator + 1

                    if number_operator == len(final_result_output):
                        cmd_log['result']['final_output'] = first_value
                cmd_log['result']['outputs'] = output_result
                return cmd_log
        except Exception as _errorException:
            cmd_log['parsing_status'] = 'ERROR'
            _strError = "MEGA PARSING COMMAND TYPE %d ERROR %s | THREAD %s" % (command_type, _errorException, self.name)
            stringhelpers.err(_strError)
            return  cmd_log



