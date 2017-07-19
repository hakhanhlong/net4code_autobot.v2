from ..model.lldp import LLDP
import datetime


class LLDPImpl():

    def __init__(self):
        pass

    def get(self, interface_id = 0):
        return LLDP.objects(interface_id=interface_id).first()

    '''def save(self, **kwargs):
        interface_id = kwargs['interface_id']
        remote_interface = kwargs['remote_interface']
        local_interface = kwargs['local_interface']
        remote_device = kwargs['remote_device']
        local_deviceid = kwargs['local_deviceid']
        #remote_interface_id = kwargs['remote_interface_id']
        local_device = kwargs['local_device']
        s = LLDP(interface_id=interface_id, remote_interface=remote_interface,
                 local_interface=local_interface, remote_device=remote_device,local_deviceid=local_deviceid,
                 data=kwargs['data'], local_device=local_device)
        return s.save()'''

    def save(self, **kwargs):
        s = LLDP()
        for k, val in kwargs.items():
            s[str(k)] = val
        return s.save()

    def update(self, **kwargs):
        interface_id = kwargs['interface_id']
        remote_interface = kwargs['remote_interface']
        local_interface = kwargs['local_interface']
        remote_device = kwargs['remote_device']
        local_deviceid = kwargs['local_deviceid']
        local_device = kwargs['local_device']
        #remote_interface_id = kwargs['remote_interface_id']
        s = LLDP.objects(interface_id=interface_id).first()
        s.data = kwargs['data']
        s.remote_interface = remote_interface
        s.local_interface = local_interface
        s.remote_device = remote_device
        s.local_deviceid = local_deviceid
        s.local_device = local_device
        #s.remote_interface_id = remote_interface_id
        s.modified = datetime.datetime.now()
        return s.save()




