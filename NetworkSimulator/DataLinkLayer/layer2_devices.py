import PhysicalLayer.devices as devices
import Utils.utils as utils

class Bridge(devices.devices):
    def __init__(self,id,address,ports=['a','b'],active=True):
        """Default Constructor For Bridges"""
        self.mac_table = {}
        self.mac_table[ports[0]] = []
        self.mac_table[ports[1]] = []
        self.ports = ports
        self.address = address
        self.id = id
        self.active = active
        self.connected_to = []
        
    def arp_res(self,msg_data,sender):
        """Responds To ARP Request By Broadcasting It To Both The Ports"""
        ret = 0
        for i in self.connected_to:
            dev = 0
            dev = i.arp_res(msg_data,self)
            if dev !=0:
                ret = dev
                self.mac_table[ret.port].append(ret.address)
        return ret

    def reply(self,msg_data,sender,ack_msg=False):
        """Responds To Message Request By Broadcasting It Proper Port If Address Learning Is Done. Else It Broadcasts To Both Ports"""
        if msg_data['header_2'][0] not in self.mac_table[sender.port]:
            self.mac_table[sender.port].append(msg_data['header_2'][0])
        if msg_data['header_2'][1] in self.mac_table[sender.port]:
            return 
        elif msg_data['header_2'][1] not in self.mac_table[sender.port]:
            #Send Message To Port 
            for i in self.connected_to:
                if i.port != sender.port:
                    i.reply(msg_data,self,ack_msg)
        else:
            msg_data,reciever = utils.arp_request(self,msg_data)
            self.mac_table[reciever.port].append(msg_data['header_2'][1])
class Switch(Bridge):
    def __init__(self,id,address,ports=['a','b','c','d','e'],active=True):
        """Default Constructor For Switches. For ACK It Inherit The Function From Bridge Class"""
        self.id = id
        self.mac_table = {}
        self.address = address
        self.ports = ports
        for i in ports:
            self.mac_table[i] = []
        self.connected_to = []
        self.active = active

    def reply(self,msg_data,sender,ack_msg=False):
        """Responds To Message Request By Broadcasting It Proper Port If Address Learning Is Done. Else It Broadcasts To All Ports"""
        if msg_data['header_2'][0] not in self.mac_table[sender.port]:
            self.mac_table[sender.port].append(msg_data['header_2'][0])
        if msg_data['header_2'][1] in self.mac_table[sender.port]:
            return 
        elif msg_data['header_2'][1] not in self.mac_table[sender.port]:
            #Send Message To Port 
            forward_port = 0
            for key in self.mac_table.keys():
                if msg_data['header_2'][1] in self.mac_table[key]:
                    forward_port = key
                    break
            for i in self.connected_to:
                if i.port == forward_port:
                    i.reply(msg_data,self,ack_msg)
        else:
            msg_data,reciever = utils.arp_request(self,msg_data)
            self.mac_table[reciever.port].append(msg_data['header_2'][1])