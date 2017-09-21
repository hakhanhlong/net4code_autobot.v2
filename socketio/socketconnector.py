from socketIO_client_nexus import SocketIO, BaseNamespace, LoggingNamespace
from socketio.socketcallback import *
import os





class IRONNamespace(BaseNamespace):
    def oncommand(self, *args):
        stringhelpers.info(str(args))


class DEFAULTNamespace(BaseNamespace):
    def on_oncommand_response(self, *args):
        stringhelpers.info(str(args))

class FLASHNamespace(BaseNamespace):
    pass

class MEGANamespace(BaseNamespace):
    pass



class SocketConnector:

    def __init__(self, server, port):
        # longhk

        self.server = server
        self.port = port

    def connect(self):

        io = SocketIO(self.server, self.port)

        iron_namespace = io.define(IRONNamespace, '/iron')
        flash_namespace = io.define(FLASHNamespace, '/flash')
        mega_namespace = io.define(MEGANamespace, '/mega')


        io.emit('login', {'app_client_secret_id': os.environ.get('SOCKBOT_APPCLIENT_SECRET'),
                          'name': 'AUTOBOT'}, callback_login)

        #login update socketid
        io.wait_for_callbacks(seconds=1)






        #io.wait()


        return dict(io=io,iron_namespace=iron_namespace, flash_namespace=flash_namespace, mega_namespace=mega_namespace)

