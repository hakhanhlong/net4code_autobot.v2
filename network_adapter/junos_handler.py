import sys
import re
import pexpect

from network_adapter.basehandler import BaseHandler
import time

class JunosHandler(BaseHandler):

    ''' junos handler to juniper network devices'''

    def __init__(self, host='', protocol='telnet', username='', password='', port=None, timeout=30):
        super().__init__(host, protocol, username, password, port, timeout)

    def execute_command(self, command_list, blanks=0, error_reporting=False, timeout=30):
        prompt = self.re_compile([
            r"^[\w\-]+@[\w\-.]+(?:\([^\)]*\))? ?[>%] *$",
            r"^[\w\-]+@[\w\-.]+(?:\([^\)]*\))? ?# *$",
            r"^\s+\^",
            r"^(?i)error:",
            r"^.*more"
        ])
        self.blank_lines(1)
        for command in command_list:
            self.session.send(command)
            index = self.session.expect_list([pexpect.TIMEOUT, prompt[2]], timeout=0.1)
            self.output_result.append(self.session.after)
            if index == 1:
                self.session.sendcontrol('u')
                if error_reporting is True:
                    self.command_error_reporter(command)
            self.session.sendline('')
            if error_reporting is True:
                while 1:
                    index = self.session.expect_list(prompt, timeout=1)
                    if index == 4:
                        self.output_result.append(self.session.after)
                        self.session.sendline('')  # send space get more information
                    else:
                        self.output_result.append(self.session.before)
                        break
            else:
                while 1:
                    index = self.session.expect_list([prompt[0], prompt[1], prompt[4]], timeout=1)
                    if index == 2:
                        self.output_result.append(self.session.after)
                        self.session.sendline('')  # send space get more information
                    else:
                        self.output_result.append(self.session.before)
                        break

            if index == 0:
                if blanks > 0: self.blank_lines(blanks)
            elif index == 1:
                pass
            else:
                self.command_error_reporter(command)
        self.blank_lines(1)
        self.session.terminate(True)

    def execute_action_command(self, command_list, blanks=0, error_reporting=False, timeout=30, terminal=True):
        self.output_result = []
        prompt = self.re_compile([
            r"^[\w\-]+@[\w\-.]+(?:\([^\)]*\))? ?[>%] *$",
            r"^[\w\-]+@[\w\-.]+(?:\([^\)]*\))? ?# *$",
            r"^\s+\^",
            r"^(?i)error:",
            r"^.*more"
        ])
        #self.blank_lines(2)
        for command in command_list:
            #self.session.send(command)
            #time.sleep(0.3)
            self.session.sendline(command)
            time.sleep(0.3)
            self.session.readline()
            '''if self.session.buffer is not '':
                self.output_result.append(self.session.buffer)
            else:
                self.output_result.append(self.session.buffer)'''

            index = self.session.expect_list([pexpect.TIMEOUT, prompt[2]], timeout=0.1)
            #self.output_result.append(self.session.buffer)
            if index == 1:
                self.session.sendcontrol('u')
                if error_reporting is True:
                    self.command_error_reporter(command)
            self.session.sendline('')
            #time.sleep(0.5)
            #self.output_result.append(self.session.buffer)
            if error_reporting is True:
                while 1:
                    index = self.session.expect_list(prompt, timeout=-1)
                    if index == 4:
                        self.session.sendline('')  # send space get more information
                        #self.output_result.append(self.session.buffer)
                    else:
                        #self.output_result.append(self.session.buffer)
                        break
            else:
                while 1:
                    index = self.session.expect_list([prompt[0], prompt[1], prompt[4]], timeout=-1)
                    if index == 2:
                        self.session.sendline('')  # send space get more information
                        #self.output_result.append(self.session.buffer)
                    else:
                        #self.session.sendline('')  # send space get more information
                        #self.output_result.append(self.session.buffer)
                        break

            if index == 0:
                if blanks > 0: self.blank_lines(blanks)
            elif index == 1:
                #time.sleep(3)
                pass
            else:
                self.command_error_reporter(command)

        #self.blank_lines(2)
        #if self.session.buffer is not '':
            #self.output_result.append(self.session.buffer)
        if terminal:
            self.session.terminate(True)

    def execute_template_action_command(self, command_list, blanks=0, error_reporting=False, timeout=30, terminal=True):
        self.output_result = []
        prompt = self.re_compile([
            r"^[\w\-]+@[\w\-.]+(?:\([^\)]*\))? ?[>%] *$",
            r"^[\w\-]+@[\w\-.]+(?:\([^\)]*\))? ?# *$",
            r"^\s+\^",
            r"^(?i)error:",
            r"^.*more"
        ])
        #self.blank_lines(2)
        for command in command_list:
            #self.session.send(command)
            #time.sleep(0.3)
            self.session.sendline(command)
            time.sleep(0.3)
            self.session.readline()
            '''if self.session.buffer is not '':
                self.output_result.append(self.session.buffer)
            else:
                self.output_result.append(self.session.buffer)'''

            index = self.session.expect_list([pexpect.TIMEOUT, prompt[2]], timeout=0.1)
            #self.output_result.append(self.session.buffer)
            if index == 1:
                self.session.sendcontrol('u')
                if error_reporting is True:
                    self.command_error_reporter(command)
            self.session.sendline('')
            #time.sleep(0.5)
            #self.output_result.append(self.session.buffer)
            if error_reporting is True:
                while 1:
                    index = self.session.expect_list(prompt, timeout=-1)
                    if index == 4:
                        self.session.sendline('')  # send space get more information
                        #self.output_result.append(self.session.buffer)
                    else:
                        #self.output_result.append(self.session.buffer)
                        break
            else:
                while 1:
                    index = self.session.expect_list([prompt[0], prompt[1], prompt[4]], timeout=-1)
                    if index == 2:
                        self.session.sendline('')  # send space get more information
                        #self.output_result.append(self.session.buffer)
                    else:
                        #self.session.sendline('')  # send space get more information
                        #self.output_result.append(self.session.buffer)
                        break

            if index == 0:
                if blanks > 0: self.blank_lines(blanks)
            elif index == 1:
                #time.sleep(3)
                pass
            else:
                self.command_error_reporter(command)

        #self.blank_lines(2)
        #if self.session.buffer is not '':
            #self.output_result.append(self.session.buffer)
        if terminal:
            self.session.terminate(True)


    def terminal(self):
        self.session.terminate(True)