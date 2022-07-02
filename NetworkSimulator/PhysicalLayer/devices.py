from NetworkLayer.router import Router
import random
import Utils.utils as utils

def generate_mac_address():
    """Grants A MAC Address To Each Of The Device"""
    mac = [str(random.randint(0xB,0x63)) for x in range(3)]
    return ("11:11:11:"+":".join(mac))
 
class devices:
    """Class For End Devices"""
    def __init__(self,id,address,ip,gateway,process,port='a',active=True):
        """Default Constructor For Devices"""
        self.id = id
        self.address = address
        self.ip = ip
        self.port = port
        self.active = active
        self.connected_to = []
        self.stored_arp = {}
        self.process = process
        self.gateway = gateway
    
    def make_inactive(self):
        """Makes The Device Inactive So Messages Cant Be Sent Or Recieved."""
        self.active = False

    def make_active(self):
        """Makes The Device active So Messages Can Be Sent Or Recieved."""
        self.active = True
    
    def arp_res(self,msg_data,sender):
        """Responds To ARP Request. If The IP Address In Frame Corresponds To The Device ,
        it Will Send Its MAC Address Back,else Request Will Be Rejected/Dropped."""
        if msg_data['header_3'][1].ip == self.ip.ip:
            print("Device {} :  Sent its MAC Address".format(self.id))
            self.stored_arp[msg_data['header_3'][0]] = msg_data['header_2'][0]
            return self
        else:
            print("Device {}: ARP Request Rejected".format(self.id))
            return 0

    def reply(self,msg_data,sender,ack_msg = False):
        """Responds To Message Request. It will send back an ACK with probability of 75%. If MAC Address Is Not The Same As Device the packet is dropped."""
        if msg_data["header_2"][1] == self.address:
            print("Devive with MAC : {} Recieved Data From Source : {} ".format(msg_data["header_2"][1],msg_data['header_2'][0]))
            if not ack_msg:
                if random.random() > 0.0:
                    print("Device {} : Sending ACK!".format(self.id))
                    utils.send_message(self,utils.generate_ack(msg_data),True)
                else:
                    print("Device {} : ACK Failed!".format(self.id))
                    utils.send_message(sender, msg_data)
        else:
            print("Device {} : Rejected The Packet".format(self.id))
            
class hubs(devices):
    def __init__(self,id,port = 'a',active=True):
        """Default Constructor For Hubs"""
        self.id = id
        self.active = active
        self.connected_to = []
        self.port = port

    def arp_res(self,msg_data,sender):
        """Broadcasts ARP Request To All The Devices Connected To It Except The One From Which Request Came."""
        ret=0
        for i in self.connected_to:
            dev = 0
            if i == sender:
                continue
            dev = i.arp_res(msg_data,self)
            if dev !=0:
                ret = dev
        return ret

    def reply(self,msg_data,sender,ack_msg=False):
        """Broadcasts Message Request To All The Devices Connected To It Except The One From Which Request Came."""
        for i in self.connected_to:
            if i==sender:
                continue
            i.reply(msg_data,self,ack_msg)

