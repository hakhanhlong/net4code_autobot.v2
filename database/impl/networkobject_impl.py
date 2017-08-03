from ..model.networkobjects import NetworkObject
import datetime


class NetworkObjectImpl():

    def __init__(self):
        pass

    def get(self, device_id = 0, table=None, column=None, row=None, command_id=None):
        s = NetworkObject.objects(device_id=device_id, column=column, table=table, row=row, command_id=command_id).first()
        return s

    def get_field(self, device_id = 0, table = None, field_name=None, field_value=None):
        s = NetworkObject.objects(__raw__={'device_id':device_id, str(field_name):str(field_value), 'table': table})
        return s

    def get_field_first(self, device_id = 0, table = None, field_name=None, field_value=None):
        s = NetworkObject.objects(__raw__={'device_id':device_id, str(field_name):str(field_value), 'table': table}).first()
        return s

    def delete(self, networkobject_id = 0):
        s = NetworkObject.objects(networkobject_id=networkobject_id).first()
        return s.delete()

    def get_list(self, device_id = 0, table=None, command_id=None):
        return NetworkObject.objects(device_id=device_id, table=table, command_id=command_id)


    def get_list_by_device_table(self, device_id = 0, table=None):
        return NetworkObject.objects(device_id=device_id, table=table)

    def save(self, **kwargs):
        s = NetworkObject()
        for k, val in kwargs.items():
            s[str(k)] = val
        return s.save()


    def update_merge(self, networkobject_id = 0, **kwargs):
        s = NetworkObject.objects(networkobject_id = networkobject_id).first()
        for k, val in kwargs.items():
            s[str(k)] = val
        s.modified = datetime.datetime.now()
        return s.save()



    def update(self, **kwargs):
        device_id = kwargs['device_id']
        column = kwargs['column']
        row = kwargs['row']
        table = kwargs['table']
        s = NetworkObject.objects(device_id=device_id, column = column, table=table, row=row).first()
        for k, val in kwargs.items():
            s[str(k)] = val
        s.modified = datetime.datetime.now()
        return s.save()