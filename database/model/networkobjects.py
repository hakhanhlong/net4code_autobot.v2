from mongoengine import *
import datetime



class NetworkObject(DynamicDocument):
    '''DynamicDocument documents work in the same way as Document but any data / attributes set to them will also be saved'''
    networkobject_id = SequenceField()
    table = StringField(max_length=255, required=True)
    device_id = IntField(default=0)
    created = DateTimeField(default=datetime.datetime.now)
    modified = DateTimeField(default=datetime.datetime.now)
    meta = {'collection': 'networkobjects'}


