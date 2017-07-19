from mongoengine import *
import datetime



class Interfaces(DynamicDocument):
    '''DynamicDocument documents work in the same way as Document but any data / attributes set to them will also be saved'''
    interface_name = StringField(max_length=255, required=True)
    interface_id = SequenceField()
    device_id = IntField(default=0)
    created = DateTimeField(default=datetime.datetime.now)
    modified = DateTimeField(default=datetime.datetime.now)
    meta = {'collection': 'interfaces'}


