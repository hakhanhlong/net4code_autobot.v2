from socketIO_client_nexus import SocketIO, BaseNamespace



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
        io.define(FLASHNamespace, '/mega')

        #io.wait()


        return io

