import sys
import re
import pexpect
import time

from network_adapter.basehandler import BaseHandler


class IOSXRHandler(BaseHandler):
    ''' ios handler to cisco network devices'''

    def __init__(self, host='', protocol='telnet', username='', password='', port=None, timeout=30,
                 socketio=None, socket_namespace=None, socket_command=None):
        super().__init__(host, protocol, username, password, port, timeout,socketio, socket_namespace, socket_command)


    '''def ios_enable(self, enable_password='', timeout=10):
        if enable_password == '': return
        prompt = self.re_compile([
            r"> *$",
            r"(?i)password: *$",
            r"(?:#|\(enable\)) *$",
        ])

        self.session.sendline('')
        index = self.session.expect_list(prompt, timeout=timeout)
        if index == 0:
            self.session.sendline('enable')
            index = self.session.expect_list(prompt, timeout=timeout)
            if index == 1:
                self.session.sendline(enable_password)
                index = self.session.expect_list(prompt, timeout=timeout)
                if index == 1:
                    self.auth_failed('enable failed.')'''

    def execute_command(self, command_list, blanks=0, error_reporting=False, timeout=30):
        prompt = self.re_compile([
            r"^[\w\-/.]+ ?[>#] *(?:\(enable\))? *$",
            r"\((?:config|cfg)[^\)]*\) ?# *$",
            r"(?i)^clear.*\[confirm\] *$",
            r"(?i)^% *(?:ambiguous|incomplete|invalid|unknown|\S+ overlaps).*$",
            r".*--More",
            r".*#"
        ])
        self.blank_lines(2)
        for command in command_list:
            self.session.sendline(command)
            self.session.readline()
            index = self.session.expect_list(prompt, timeout=timeout)
            self.output_result.append(self.session.before)
            self.output_result.append(self.session.after)
            if index == 0:
                if blanks > 0: self.blank_lines(blanks)
            elif index == 1:
                self.output_result.append(self.session.before)
                pass
            elif index == 2:
                self.session.sendline('')
                self.session.expect_list(prompt, timeout=timeout)
                self.output_result.append(self.session.before)
                if blanks > 0: self.blank_lines(blanks)
            elif index == 3:
                if error_reporting is True:
                    self.command_error_reporter(command)
                else:
                    self.session.sendcontrol('u')
                    self.session.sendline('')
                    index = self.session.expect_list(prompt, timeout=timeout)
                    self.output_result.append(self.session.after)
                    if index == 0:
                        if blanks > 0: self.blank_lines(blanks)
            elif index == 4 or index == 5:  # xu ly more
                self.session.sendline(' ')
                while 1:
                    time.sleep(0.2)
                    index = self.session.expect_list([pexpect.TIMEOUT, prompt[4]], timeout=1)
                    if index == 1:
                        self.session.sendline(' ')
                        self.output_result.append(self.session.after)
                    else:
                        self.output_result.append(self.session.before)
                        break

                        # print("longhk:", self.session.before)

        self.blank_lines(2)
        self.session.terminate(True)

    def execute_action_command(self, command_list, blanks=0, error_reporting=False, timeout=30, terminal=True):
        self.output_result = []
        prompt = self.re_compile([
            r"^[\w\-/.]+ ?[>#] *(?:\(enable\))? *$",
            r"\((?:config|cfg)[^\)]*\) ?# *$",
            r"(?i)^clear.*\[confirm\] *$",
            r"(?i)^% *(?:ambiguous|incomplete|invalid|unknown|\S+ overlaps).*$",
            r".*--More",
            r".*#"
        ])
        #self.blank_lines(2)
        for command in command_list:
            self.session.sendline(command)
            time.sleep(0.3)
            self.session.readline()
            index = self.session.expect_list(prompt, timeout=timeout)

            if index == 0:
                if blanks > 0: self.blank_lines(blanks)
            elif index == 1:
                pass
            elif index == 2:
                self.session.sendline('')
                self.session.expect_list(prompt, timeout=timeout)
                if blanks > 0: self.blank_lines(blanks)
            elif index == 3:
                if error_reporting is True:
                    self.command_error_reporter(command)
                else:
                    self.session.sendcontrol('u')
                    self.session.sendline('')
                    index = self.session.expect_list(prompt, timeout=timeout)
                    if index == 0:
                        if blanks > 0: self.blank_lines(blanks)
            elif index == 4 or index == 5:  # xu ly more
                self.session.sendline(' ')
                while 1:
                    time.sleep(0.2)
                    index = self.session.expect_list([pexpect.TIMEOUT, prompt[4]], timeout=1)
                    if index == 1:
                        self.session.sendline(' ')
                    else:
                        break
            elif index == 5:
                pass
            elif index == 6:
                pass


        #self.blank_lines(2)
        #if self.session.buffer is not '':
            #self.output_result.append(self.session.buffer)


        if terminal:
            self.session.terminate(True)



    def execute_template_action_command(self, command_list, blanks=0, error_reporting=False, timeout=30, terminal=True):
        self.output_result = []
        prompt = self.re_compile([
            r"^[\w\-/.]+ ?[>#] *(?:\(enable\))? *$",
            r"\((?:config|cfg)[^\)]*\) ?# *$",
            r"(?i)^clear.*\[confirm\] *$",
            r"(?i)^% *(?:ambiguous|incomplete|invalid|unknown|\S+ overlaps).*$",
            r".*--More",
            r".*#"
        ])
        #self.blank_lines(2)
        for command in command_list:
            self.session.sendline(command)
            time.sleep(0.3)
            self.session.readline()
            index = self.session.expect_list(prompt, timeout=timeout)

            if index == 0:
                if blanks > 0: self.blank_lines(blanks)
            elif index == 1:
                pass
            elif index == 2:
                self.session.sendline('')
                self.session.expect_list(prompt, timeout=timeout)
                if blanks > 0: self.blank_lines(blanks)
            elif index == 3:
                if error_reporting is True:
                    self.command_error_reporter(command)
                else:
                    self.session.sendcontrol('u')
                    self.session.sendline('')
                    index = self.session.expect_list(prompt, timeout=timeout)
                    if index == 0:
                        if blanks > 0: self.blank_lines(blanks)
            elif index == 4 or index == 5:  # xu ly more
                self.session.sendline(' ')
                while 1:
                    time.sleep(0.2)
                    index = self.session.expect_list([pexpect.TIMEOUT, prompt[4]], timeout=1)
                    if index == 1:
                        self.session.sendline(' ')
                    else:
                        break
            elif index == 5:
                pass
            elif index == 6:
                pass


        #self.blank_lines(2)
        #if self.session.buffer is not '':
            #self.output_result.append(self.session.buffer)


        if terminal:
            self.session.terminate(True)


    def terminal(self):
        self.session.terminate(True)



