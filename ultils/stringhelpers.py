import textwrap
import random
import string

HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = "\033[1m"

def generate_random_keystring(length):
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))


def print_bold(msg, end='\n', socketio=None, socket_namespace=None, on_command_text=None):
    """ print a string in 'bold' font """
    _msg = "\033[1m" + msg + "\033[0m"
    print(_msg, end=end)
    if socketio is not None:
        socketio.emit(on_command_text, _msg)

    if socket_namespace is not None:
        socket_namespace.emit(on_command_text, _msg)





def print_welcome():
    str_welcome = '''
               AAA           UUUUUUUU     UUUUUUUUTTTTTTTTTTTTTTTTTTTTTTT     OOOOOOOOO     BBBBBBBBBBBBBBBBB        OOOOOOOOO     TTTTTTTTTTTTTTTTTTTTTTT
              A:::A          U::::::U     U::::::UT:::::::::::::::::::::T   OO:::::::::OO   B::::::::::::::::B     OO:::::::::OO   T:::::::::::::::::::::T
             A:::::A         U::::::U     U::::::UT:::::::::::::::::::::T OO:::::::::::::OO B::::::BBBBBB:::::B  OO:::::::::::::OO T:::::::::::::::::::::T
            A:::::::A        UU:::::U     U:::::UUT:::::TT:::::::TT:::::TO:::::::OOO:::::::OBB:::::B     B:::::BO:::::::OOO:::::::OT:::::TT:::::::TT:::::T
           A:::::::::A        U:::::U     U:::::U TTTTTT  T:::::T  TTTTTTO::::::O   O::::::O  B::::B     B:::::BO::::::O   O::::::OTTTTTT  T:::::T  TTTTTT
          A:::::A:::::A       U:::::D     D:::::U         T:::::T        O:::::O     O:::::O  B::::B     B:::::BO:::::O     O:::::O        T:::::T
         A:::::A A:::::A      U:::::D     D:::::U         T:::::T        O:::::O     O:::::O  B::::BBBBBB:::::B O:::::O     O:::::O        T:::::T
        A:::::A   A:::::A     U:::::D     D:::::U         T:::::T        O:::::O     O:::::O  B:::::::::::::BB  O:::::O     O:::::O        T:::::T
       A:::::A     A:::::A    U:::::D     D:::::U         T:::::T        O:::::O     O:::::O  B::::BBBBBB:::::B O:::::O     O:::::O        T:::::T
      A:::::AAAAAAAAA:::::A   U:::::D     D:::::U         T:::::T        O:::::O     O:::::O  B::::B     B:::::BO:::::O     O:::::O        T:::::T
     A:::::::::::::::::::::A  U:::::D     D:::::U         T:::::T        O:::::O     O:::::O  B::::B     B:::::BO:::::O     O:::::O        T:::::T
    A:::::AAAAAAAAAAAAA:::::A U::::::U   U::::::U         T:::::T        O::::::O   O::::::O  B::::B     B:::::BO::::::O   O::::::O        T:::::T
   A:::::A             A:::::AU:::::::UUU:::::::U       TT:::::::TT      O:::::::OOO:::::::OBB:::::BBBBBB::::::BO:::::::OOO:::::::O      TT:::::::TT
  A:::::A               A:::::AUU:::::::::::::UU        T:::::::::T       OO:::::::::::::OO B:::::::::::::::::B  OO:::::::::::::OO       T:::::::::T
 A:::::A                 A:::::A UU:::::::::UU          T:::::::::T         OO:::::::::OO   B::::::::::::::::B     OO:::::::::OO         T:::::::::T
AAAAAAA                   AAAAAAA  UUUUUUUUU            TTTTTTTTTTT           OOOOOOOOO     BBBBBBBBBBBBBBBBB        OOOOOOOOO           TTTTTTTTTTT
    '''
    info(str_welcome)


def info_green(msg, end='\n', socketio=None, socket_namespace=None, on_command_text=None):
    _msg = OKGREEN + msg + ENDC
    print(_msg, end=end)
    if socketio is not None:
        socketio.emit(on_command_text, _msg)

    if socket_namespace is not None:
        socket_namespace.emit(on_command_text, _msg)

def info(msg, end='\n', socketio=None, socket_namespace=None, on_command_text=None):
    _msg = OKBLUE + msg + ENDC
    print(_msg, end=end)
    if socketio is not None:
        socketio.emit(on_command_text, _msg)

    if socket_namespace is not None:
        socket_namespace.emit(on_command_text, _msg)


def warn(msg, end='\n', socketio=None, socket_namespace=None, on_command_text=None):
    _msg = WARNING + msg + ENDC
    print(_msg, end=end)
    if socketio is not None:
        socketio.emit(on_command_text, _msg)

    if socket_namespace is not None:
        socket_namespace.emit(on_command_text, _msg)


def err(msg, end='\n', socketio=None, socket_namespace=None, on_command_text=None):


    _msg = FAIL + msg + ENDC
    print(_msg, end=end)
    if socketio is not None:
        socketio.emit(on_command_text, _msg)

    if socket_namespace is not None:
        socket_namespace.emit(on_command_text, _msg)


'''move text to each row'''
def text_to_arrayrow(text):
    return text.splitlines()

'''get list string between'''
def list_string_between(source, start = None, end = None):
    start_sep = start
    end_sep = end
    result = []
    tmp = source.split(start_sep)
    for par in tmp:
        if end_sep in par:
            result.append(par.split(end_sep)[0])
    return result

'''get string between'''
def string_between(source, start, end):
    try:
        result = source[source.find(start) + len(start):source.rfind(end)]
        if end == '':
            result = source[source.find(start) + len(start):len(source)]
        return result
    except ValueError:
        return None

'''find string between'''
def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        result =  s[start:end]

        if result == '' or result == None:
            if last == '':
                end = len(s)
                result = s[start:end]

        return result

    except Exception:
        return None


'''find string between keep start_by'''
def find_between_keep_str_start( s, first, last ):
    try:
        start = s.index( first )
        end = s.index( last, start )
        return s[start:end]
    except Exception:
        return None


'''find string between right'''
def find_between_r( s, first, last ):
    try:
        start = s.rindex( first ) + len( first )
        end = s.rindex( last, start )
        return s[start:end]
    except ValueError:
        return ""

def remove_duplicates(values):
    output = []
    duplicate = []
    seen = set()
    remove_duplicate = None
    for value in values:
        # If value has not been encountered yet,
        # ... add it to both list and set.
        if value not in seen:
            output.append(value)
            seen.add(value)
        else:
            duplicate.append(value)
    for dup in duplicate:
        for out in output:
            if dup == out:
                output.remove(dup)
    return output

import time
import sys
def countdown(t):
    for remaining in range(t, 0, -1):
        sys.stdout.write("\r")
        sys.stdout.write("{:2d} seconds remaining.".format(remaining))
        sys.stdout.flush()
        time.sleep(1)
