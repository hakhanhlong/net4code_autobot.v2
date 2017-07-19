import threading
import time
from ultils import stringhelpers
from api.request_helpers import RequestHelpers
from api.request_url import RequestURL
from .megastuff.megacommand import MegaCommand
from .megastuff.megaaction import MegaAction
from .megastuff.megatemplate import MegaTemplate
from .megastuff.megadiscovery import MegaDiscovery


class MegaManager(threading.Thread):
    """ Thread management mega thread """
    def __init__(self, name, is_stop):
        threading.Thread.__init__(self)
        self.name = name
        self.is_stop = is_stop
        self.counter = 0
        self.requestURL = RequestURL()


    def run(self):
        _request = RequestHelpers()
        dict_command = dict()
        dict_action = dict()
        dict_template = dict()
        dict_template_discovery = dict()
        while not self.is_stop:
            try:
                self.counter = self.counter + 1
                stringhelpers.print_bold("Archieving info MEGA number: %d" % self.counter)

                #--------------- MEGA RUN COMMAND TEST -----------------------------------------------------------------
                _request.url = self.requestURL.MEGA_URL_LIST_COMMAND_UNTESTED
                _list_commands = _request.get().json()
                if len(_list_commands) > 0:
                    for x in _list_commands:
                        key_command = 'command_%d' % (x['command_id'])
                        if dict_command.get(key_command, None) is not None:
                            pass
                        else:
                            dict_command[key_command] = key_command
                            mega_command = MegaCommand("Thread-Command-%d" % (x['command_id']), x, dict_command)
                            mega_command.start()
                time.sleep(10)
                #-------------------------------------------------------------------------------------------------------

                #-------------- MEGA RUN ACTION TEST -------------------------------------------------------------------
                _request.url = self.requestURL.MEGA_URL_LIST_ACTION_UNTESTED
                _list_actions = _request.get().json()
                if len(_list_actions) > 0:
                    for x in _list_actions:
                        key_action = 'action_%d' % (x['action_id'])
                        if dict_action.get(key_action, None) is not None:
                            pass
                        else:
                            dict_action[key_action] = key_action
                            mega_action = MegaAction("Thread-Action-%d" % (x['action_id']), x, dict_action)
                            mega_action.start()
                time.sleep(10)
                #-------------------------------------------------------------------------------------------------------

                #-------------- MEGA RUN TEMPLATE TEST ----------------------------------------------------------------
                _request.url = self.requestURL.MEGA_URL_LIST_TEMPLATE_UNTESTED
                _list_templates = _request.get().json()
                #_list_templates = [_request.get().json()]
                if len(_list_templates) > 0:
                    for x in _list_templates:
                        key_template = 'template_%d' % (x['template_id'])
                        if dict_template.get(key_template, None) is not None:
                            pass
                        else:
                            dict_template[key_template] = key_template
                            mega_template = MegaTemplate("Thread-Template-%d" % (x['template_id']), x, dict_template)
                            mega_template.start()
                    pass
                # ---------------------------------------------------------------------------------------------------------
                time.sleep(10)

                #-------------- MEGA RUN TEMPLATE TEST ----------------------------------------------------------------
                '''_request.url = self.requestURL.MEGA_URL_TEMPLATE_DISCOVERY
                #_list_templates = _request.get().json()
                _list_templates_descovery = [_request.get().json()]
                if len(_list_templates_descovery) > 0:
                    for x in _list_templates_descovery:
                        key_template = 'template_discovery_%d' % (x['template_id'])
                        #if dict_template_discovery.get(key_template, None) is not None:
                        #    pass
                        #else:
                        dict_template_discovery[key_template] = key_template
                        mega_template_discovery = MegaDiscovery("Thread-Discovery-Template-%d" % (x['template_id']), x, dict_template_discovery)
                        mega_template_discovery.start()
                    pass'''
                # ---------------------------------------------------------------------------------------------------------
                #time.sleep(90)



            except Exception as e:
                stringhelpers.err("MEGA MAIN THREAD ERROR %s" % (e))
            except ConnectionError as errConn:
                stringhelpers.err("MEGA CONNECT API ERROR %s" % (errConn))


    def stop(self):
        self.is_stop = True
