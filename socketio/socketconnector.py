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

        io.define(IRONNamespace, '/iron')
        io.define(FLASHNamespace, '/flash')
        io.define(MEGANamespace, '/mega')


        io.emit('login', {'app_client_secret_id': os.environ.get('APPCLIENT_SECRET'), 'name': 'AUTOBOT'}, callback_login)
        io.wait_for_callbacks(seconds=1)


        #io.wait()


        return io

