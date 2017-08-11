import pexpect
import sys
import re
import os


class BaseHandler:
    def __init__(self, host='', protocol='telnet', username='', password='', port=None, timeout=30):
        self.host = host
        self.protocol = protocol.lower()
        self.username = username
        self.password = password
        self.port = port
        self.timeout = timeout
        self.output_result = []



        if 'tel' in self.protocol:
            if self.port == None:
                self.port = 23
            cmd = "telnet {0} {1}".format(self.host, self.port)
        elif 'ssh' in self.protocol:
            if self.port == None:
                self.port = 22
            opt = "-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o KexAlgorithms=+diffie-hellman-group1-sha1"
            # opt = "-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"
            cmd = "ssh {0} {1}@{2} -p {3}".format(opt, self.username, self.host, self.port)



        self.session = pexpect.spawnu(cmd, timeout=self.timeout, maxread=1024 * 2, searchwindowsize=1024 * 4, encoding='utf8')

    def auth_failed(self, message):
        self.session.terminate()
        print(message)
        sys.exit()

    def command_error_reporter(self, command):
        print("\nCommand error detected at '{}'.".format(command))
        print("Press '^]' to resume.")
        print(self.session.match.group(0), self.session.interact())

    def re_compile(self, patterns):
        return [re.compile(pattern, re.S | re.M) for pattern in patterns]

    def login(self, timeout=10):
        prompt = self.re_compile([
            r"(?i)(?:username|login): *$",
            r"(?i)password: *$",
            r"[>#$%] *$"
        ])
        try:
            index = self.session.expect_list(prompt, timeout=timeout)
        except:
            error = sys.exc_info()
            try:
                self.session.sendcontrol('m') #Press Enter Key
                index = self.session.expect_list(prompt, timeout=timeout)
            except:
                self.session.terminate()
                print("Connect error at '{}, port {}'.\n".format(self.host, self.port))
                print(self.session.before)
                sys.exit()
                return False

        if index == 0:
            self.session.sendline(self.username)
            index = self.session.expect_list(prompt, timeout=timeout)
            if index != 1:
                self.auth_failed('login failed.')
                return False
        if index == 1:
            self.session.sendline(self.password)
            index = self.session.expect_list(prompt, timeout=timeout)
            if index != 2:
                self.auth_failed('login failed.')
                return False
        result = True
        if result:
            print("Connect SUCCESS at '{}, port {}'.\n".format(self.host, self.port))
            return True

    def logout(self):
        self.session.sendline('exit')
        if self.session.isalive():
            self.session.sendline('exit')
        self.session.expect(pexpect.EOF)
        self.session.close()

    def is_alive(self):
        return self.session.isalive()

    def log(self, logfile=''):
        #if logfile:
        self.session.logfile = open(logfile, 'w')
        #else:
        self.session.logfile_read = sys.stdout

    def log_standard(self, logfile=''):
        if logfile:
            self.session.logfile = open(logfile, 'w')
        else:
            self.session.logfile_read = sys.stdout



    #-----------------------------------------------------------------------------------------------


    def blank_lines(self, blanks):
        for i in range(blanks):
            self.session.sendline('')
            self.session.readline()



    def get_output(self):
        result = self.output_result
        result = ''.join(map(str, result))
        result = result.replace("--More--", "")
        result = result.replace("--More - -", "")
        result = result.replace("[K            [K", "")
        result = result.replace("[K", "")
        result = result.replace("          ", "")
        result = result.replace("         ", "")


        if "---(more)---" in result: #process replace junos
            for i in range(101):
                result = result.replace("---(more "+str(i)+"%)---", "")

            result = result.replace("---(more)---", "")
            result = result.replace("\r                                        \r", "")

        result = result.replace("--More", "")
        #result = result.replace("--", "")
        result = result.replace("[K", "")
        result = result.replace("[K", "")
        result = result.replace("[K --More", "")
        result = result.replace("--           [K", "")
        result = result.replace("           ", "")
        return result


    def get_action_output(self, filelog=None):

        try:

            result = open(filelog, 'r')
            result = result.read()


            result = result.replace("--More--", "")
            result = result.replace("--More - -", "")
            result = result.replace("[K            [K", "")
            result = result.replace("[K", "")
            result = result.replace("          ", "")
            result = result.replace("         ", "")

            if "---(more)---" in result:  # process replace junos
                for i in range(101):
                    result = result.replace("---(more " + str(i) + "%)---", "")

                result = result.replace("---(more)---", "")
                result = result.replace("\r                                        \r", "")

            result = result.replace("--More", "")
            #result = result.replace("--", "")
            result = result.replace("[K", "")
            result = result.replace("[K", "")
            result = result.replace("[K --More", "")
            result = result.replace("--           [K", "")
            result = result.replace("           ", "")
            result = result.replace("          [K     ", "")
            result = result.replace("", "")
            result = result.replace("\00", "")


            open(filelog, "w").close()

            return result
        except Exception as error:
            pass

    def remove_file_log(self, filelog=None):
        os.remove(filelog)






