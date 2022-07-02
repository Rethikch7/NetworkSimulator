from netaddr.ip import IPAddress, IPNetwork
# import PhysicalLayer.devices as devices
class Router():
    def __init__(self,id,num_interface,active=True):
        self.id = id
        self.num_interface = num_interface
        self.interface = [0]*num_interface
        self.active = active
        self.connected_to_interface = [0]* num_interface
        self.router_table = {}
        self.stored_arp = {}
    
    def make_active(self):
        self.active = True
    def make_inactive(self):
        self.active = False

    def init_rip(self):
        for i in range(len(self.interface)):
            if self.interface[i] == 0:
                continue
            self.router_table[self.interface[i][0].network]= [0,self.interface[i][0].netmask,i,'-']

    def arp_res(self,msg_data,device):
        if msg_data['header_3'][1].network == msg_data['header_3'][0].network:
            print("Router {} rejected the ARP Request".format(self.id))
            return 0
        return 0

    def arp_request(self,msg_data,interface):
        """ARP Request Method To Get MAC Address Using IP Address Of Receiver"""
        ret = 0
        print("ARP Request Sent By Device {}".format(self.id))
        i = self.connected_to_interface[interface]
        ret = i.arp_res(msg_data,self)
        msg_data['header_2'].append(ret.address)
        print(msg_data)
        return msg_data
    def check_longest_mask(self,mask,val):
        minimum = val
        for key,value in self.router_table.items():
            if key ==mask:
                if value[2] < val[2]:
                    minimum = value
        return minimum
    def reply(self,msg_data,sender,ack_msg = False):
        print("Message At Router {}".format(self.id))
        if msg_data['header_3'][1].network == msg_data['header_3'][0].network:
            print("Packet Rejected By Router {}".format(self.id))
            self.stored_arp[msg_data['header_3'][0]] = msg_data['header_2'][0]
            self.stored_arp[msg_data['header_3'][1]] = msg_data['header_2'][1]
            return
        elif msg_data['header_3'][1].network not in self.router_table.keys():
            print("No Hop Available")
            return
        else:
            for i in self.router_table:
                if msg_data['header_3'][1].network == i:
                    if self.router_table[i][-1] == '-' and msg_data['header_3'][1] not in self.stored_arp.keys():
                        msg_data = self.arp_request(msg_data,self.router_table[i][2])
                        self.stored_arp[msg_data['header_3'][1]] = msg_data['header_2'][1]
                        self.stored_arp[msg_data['header_3'][0]] = msg_data['header_2'][0]
                        return self.connected_to_interface[self.router_table[i][2]].reply(msg_data,self,ack_msg)
                    return self.connected_to_interface[self.router_table[i][-1]].reply(msg_data,self,ack_msg)
    def find_interface(self,device):
        for i in range(len(self.connected_to_interface)):
            if self.connected_to_interface[i]==device:
                return i
        return -1
    def make_RIP_table(self,list_of_routers):
        for _ in range(len(list_of_routers)):
            for j in list_of_routers:
                if j==self:
                    continue
                # if j not in self.connected_to_interface:
                #     continue
                for k,v in j.router_table.items():
                    if (k not in self.router_table.keys()) or (k in self.router_table.keys() and self.router_table[k][-1]==-1):
                        if self.find_interface(j) !=-1:
                            self.router_table[k] = [v[0]+1,v[1],v[2],self.find_interface(j)]
                    else:
                        if self.router_table[k][0] > v[0]+1:
                            self.router_table[k] = [v[0]+1,v[1],v[2],self.find_interface(j)]
    def config_interface_ip(self,int_id,ip):
        self.interface[int_id] = [ip,"Random MAC Address"]

# r1 = Router(0,3)
# r2 = Router(1,3)
# r3 = Router(2,3)
# lr = [r1,r2,r3]
# r1.config_interface_ip(0,IPNetwork('10.0.0.1/8'))
# r1.config_interface_ip(1,IPNetwork('20.0.0.1/8'))
# r2.config_interface_ip(0,IPNetwork('40.0.0.1/8'))
# r2.config_interface_ip(1,IPNetwork('30.0.0.1/8'))
# r3.config_interface_ip(0,IPNetwork('20.0.0.2/8'))
# r3.config_interface_ip(1,IPNetwork('30.0.0.2/8'))
# r1.init_rip()
# r2.init_rip()
# r3.init_rip()
# print(r1.router_table)
# print(r2.router_table)
# print(r3.router_table)
# r1.make_RIP_table(lr)
# print(r1.router_table)
# r2.make_RIP_table(lr)
# print(r2.router_table)
# r3.make_RIP_table(lr)
# print(r3.router_table)