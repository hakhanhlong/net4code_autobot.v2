from mongoengine import *
from ..model.tables import TABLE

import datetime

class TABLEImpl():
    def __init__(self):
        pass

    def get(self, table_id = None):
        '''get table by table_id'''
        return TABLE.objects(table_id=table_id).first()