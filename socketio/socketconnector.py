from socketIO_client_nexus import SocketIO, BaseNamespace
from socketio.socketcallback import *
import os





class IRONNamespace(BaseNamespace):
    pass

class FLASHNamespace(BaseNamespace):
    pass

class MEGANamespace(BaseNamespace):
    pass





class SocketConnector:

    def __init__(self, server, port):


        self.server = server
        self.port = port

    def connect(self):

        io = SocketIO(self.server, self.port)

        iron_namespace = io.define(IRONNamespace, '/iron')
        flash_namespace = io.define(FLASHNamespace, '/flash')
        mega_namespace = io.define(MEGANamespace, '/mega')


        io.emit('login', {'app_client_secret_id': os.environ.get('SOCKBOT_APPCLIENT_SECRET'),
                          'name': 'AUTOBOT'}, callback_login)
        io.wait_for_callbacks(seconds=1)

        iron_namespace.on('on_command', on_iron_command)
        io.wait(seconds=1)


        #io.wait()


        return dict(io=io,iron_namespace=iron_namespace, flash_namespace=flash_namespace, mega_namespace=mega_namespace)

