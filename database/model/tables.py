from mongoengine import *
import datetime



class TABLE(DynamicDocument):
    '''DynamicDocument documents work in the same way as Document but any data / attributes set to them will also be saved'''
    table_id = SequenceField()
    created = DateTimeField(default=datetime.datetime.now)
    modified = DateTimeField(default=datetime.datetime.now)
    meta = {'collection': 'tables'}