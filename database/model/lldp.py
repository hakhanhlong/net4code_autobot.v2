from mongoengine import *
import datetime



class LLDP(DynamicDocument):
    '''DynamicDocument documents work in the same way as Document but any data / attributes set to them will also be saved'''
    interface_id = IntField()
    remote_interface = StringField(max_length=255, required=True)
    #remote_interface_id = IntField()
    local_interface = StringField(max_length=255, required=True)
    remote_device = StringField(max_length=255, required=True)
    created = DateTimeField(default=datetime.datetime.now)
    modified = DateTimeField(default=datetime.datetime.now)
    meta = {'collection': 'lldp'}