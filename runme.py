from os.path import join, dirname
from dotenv import load_dotenv
from ultils import stringhelpers
from fang.mega import MegaManager
from fang.ironman import IronManager
from fang.flask import FlaskManager
import os

from mongoengine import connect

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

from socketio.socketconnector import SocketConnector

import logging
logging.getLogger('socketIO-client-nexus').setLevel(logging.DEBUG)
logging.basicConfig()



def main():

    connect(host="mongodb://27.78.16.56:8040/iron_man")
    #connect(host="mongodb://27.78.16.56:8040/ironmanV2")

    stringhelpers.print_welcome()



    socketConnector = SocketConnector(os.environ.get('SOCKBOT_SERVER'), os.environ.get('SOCKBOT_PORT'))
    dict_sockbot = socketConnector.connect()

    '''_mega_manager = MegaManager('MEGA-MANAGEMENT', False)
    _mega_manager.start()

    _flask_manager = FlaskManager('FLASK-MANAGEMENT', False)
    _flask_manager.start()'''

    _ironman_manager = IronManager('IRONMAN-MANAGEMENT', False, dict_sockbot['iron_namespace'])
    _ironman_manager.start()


if __name__ == '__main__':
    main()
