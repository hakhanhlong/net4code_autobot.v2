from network_adapter.ios_handler import IOSHandler
from network_adapter.ios_xr_handler import IOSXRHandler
from network_adapter.junos_handler import JunosHandler
import sys
from ultils import stringhelpers

class FactoryConnector:
    ''' Factory connector management'''
    def __init__(self, device_type, host='', protocol='telnet', username='', password='', port=None, timeout=30):
        self.device_type = device_type
        self.host = host
        self.protocol = protocol
        self.username = username
        self.password = password
        self.port = port,
        self.timeout = timeout
        self.file_log_command = "%s.log" % (stringhelpers.generate_random_keystring(10))
        self.device_id = None

    def execute(self, commands=[]):

        parameters = {
            'host': self.host,
            'protocol': self.protocol,
            'username': self.username,
            'password': self.password,
            'port': self.port[0],
            'timeout': self.timeout
        }
        if 'ios' == self.device_type:
            ios = IOSHandler(**parameters)
            ios.login()
            ios.log(self.file_log_command)
            ios.execute_command(commands, blanks = 2, error_reporting = True)
            #result = ios.get_output()
            #ios.logout()
            return ios
        if 'ios-xr' == self.device_type:
            ios = IOSXRHandler(**parameters)
            ios.login()
            ios.log(self.file_log_command)
            #ios.read_result()
            ios.execute_command(commands, blanks = 2, error_reporting = True)
            #result = ios.get_output()
            #ios.logout()
            return ios
        elif 'junos' == self.device_type:
            junos = JunosHandler(**parameters)
            junos.login()
            junos.log(self.file_log_command)
            junos.execute_command(commands, blanks=2, error_reporting=True)
            #junos.execute_command(commands, blanks=2, error_reporting=False)
            #result = junos.get_output()
            #junos.logout()
            return junos

    def execute_keep_alive(self, loginfo=''):

        parameters = {
            'host': self.host,
            'protocol': self.protocol,
            'username': self.username,
            'password': self.password,
            'port': self.port[0],
            'timeout': self.timeout
        }
        if 'ios' == self.device_type:
            ios = IOSHandler(**parameters)
            ios.login()
            ios.log(loginfo)
            #ios.execute_command(commands, blanks = 2, error_reporting = True)
            #result = ios.get_output()
            #ios.logout()
            return ios
        if 'ios-xr' == self.device_type:
            ios = IOSXRHandler(**parameters)
            ios.login()
            ios.log(loginfo)
            #ios.read_result()
            #ios.execute_command(commands, blanks = 2, error_reporting = True)
            #result = ios.get_output()
            #ios.logout()
            return ios
        elif 'junos' == self.device_type:
            junos = JunosHandler(**parameters)
            junos.login()
            junos.log(loginfo)
            #junos.execute_command(commands, blanks=2, error_reporting=True)
            #junos.execute_command(commands, blanks=2, error_reporting=False)
            #result = junos.get_output()
            #junos.logout()
            return junos
