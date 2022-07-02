import PhysicalLayer.devices as devices
import networkx as nx
import matplotlib.pyplot as plt
import DataLinkLayer.layer2_devices as layer2_devices
import Utils.utils as utils
import threading
import time
import NetworkLayer.router as router
from netaddr import IPNetwork
import ApplicationLayer.process as process

class Network:
    """Basic Interface Class Where All Devices And Initialized To Form A Network Engine."""
    def __init__(self):
        """Default Constructor"""
        self.device_counter = 0
        self.hubs_counter = 0
        self.bridges_counter = 0
        self.switches_counter = 0
        self.router_counter = 0
        self.list_of_devices = []
        self.deivces_counter = 0
        self.network_graph = []

    def add_device(self,device):
        """Method To Add End Devices To Interface"""
        self.device_counter += 1
        self.list_of_devices.append(device)
        self.deivces_counter += 1
        self.network_graph.append([])

    def add_hub(self,hub):
        """Method To Add Hubs To Interface"""
        self.hubs_counter += 1
        self.list_of_devices.append(hub)
        self.deivces_counter += 1
        self.network_graph.append([])

    def add_bridge(self,bridge):
        """Method To Add Bridge To Interface"""
        self.bridges_counter += 1
        self.list_of_devices.append(bridge)
        self.deivces_counter += 1
        self.network_graph.append([])

    def add_switch(self,swtich):
        """Method To Add Switch To Interface"""
        self.switches_counter += 1
        self.list_of_devices.append(swtich)
        self.deivces_counter += 1
        self.network_graph.append([])
    
    def add_router(self,router):
        """Method To Add Router To Interface"""
        self.router_counter+=1
        self.list_of_devices.append(router)
        self.deivces_counter+=1
        self.network_graph.append([])

    def check_valid_device(self,d1,d2):
        """Checks If Device Id Exists."""
        if d1 >= self.deivces_counter or d2 >= self.deivces_counter:
            raise Exception("Device Dosent Exist! Please Enter Valid Device Numbers.")

    def check_device_status(self,d1,d2):
        """Checks If Both Devices Are Active"""
        if not ((self.list_of_devices[d1].active) and (self.list_of_devices[d2].active)):
            raise Exception("Device Not Active. Please Check Device Status")

    def check_connection(self,d1,d2):
        """Checks If Connection Between Devices Exists Or Not"""
        #Check if it is possible to send msg_data via any connection.
        for i in self.network_graph[d1]:
            if type(i) == devices.hubs:
                i.broadcast(d1,d2)
                break
        if self.list_of_devices[d2] in self.network_graph[d1]:
            return
        else:
            raise Exception("No Connection Between Two Devices!")

    def connect_devices(self,d1,d2,interface=-1):
        """Method To Make Connection Between Two Devices. Takes Devices ID as inputs."""
        try:
            self.check_valid_device(d1,d2)
            self.network_graph[d1].append(self.list_of_devices[d2])
            self.network_graph[d2].append(self.list_of_devices[d1])
            if type(self.list_of_devices[d1])== router.Router:
                self.list_of_devices[d1].connected_to_interface[interface] = self.list_of_devices[d2]
            else:
                self.list_of_devices[d1].connected_to.append(self.list_of_devices[d2])
            if type(self.list_of_devices[d2])== router.Router:
                self.list_of_devices[d2].connected_to_interface[interface] = self.list_of_devices[d1]
            else:
                self.list_of_devices[d2].connected_to.append(self.list_of_devices[d1])                
        except Exception as e:
            print("Invalid Input! Please Check And Enter Again!")
            print(e)

    def send_msg(self,sender_device,receiver_device,text,window_size,sequence=-1):
        """Method To Send Message. Take Sender And Receiver Id along with msg_data to send and window size to be used. Uses Stop And Wait ARQ."""
        global token
        while token!=sender_device:
            print("Device {} is currently using the token. Waiting For Access".format(token))
            time.sleep(0.5)
        print("Device {} has the token.".format(sender_device))
        seq = 0
        for m in text.split():
            msg_data = utils.make_packets(self.list_of_devices[sender_device],self.list_of_devices[receiver_device],m)
            if(self.list_of_devices[sender_device].ip.network != self.list_of_devices[receiver_device].ip.network):
                msg_data['Seq'] = 1
                print("Sending Packet To Default Gateway {}".format(self.list_of_devices[sender_device].gateway))
                for i in self.list_of_devices[sender_device].connected_to:
                    if type(i) == layer2_devices.Switch or type(i)==devices.hubs:
                        for j in i.connected_to:
                            if type(j) == router.Router:
                                return j.reply(msg_data,self.list_of_devices[sender_device])
                    elif type(i) == router.Router:
                            return i.reply(msg_data,self.list_of_devices[sender_device])            
            #Make Check If Device Is In Same Network Or Not:  TODO: SUBNET FOR ROUTERS!
            if self.list_of_devices[receiver_device].ip in self.list_of_devices[sender_device].stored_arp.keys():
                msg_data['header_2'].append(self.list_of_devices[sender_device].stored_arp[self.list_of_devices[receiver_device].ip.ip])
            else:
                msg_data = utils.arp_request(self.list_of_devices[sender_device],msg_data)
                self.list_of_devices[sender_device].stored_arp[self.list_of_devices[receiver_device].ip.ip] = self.list_of_devices[receiver_device].address
            try:
                if len(msg_data['header_2']) == 1:
                    raise Exception("NO Connection Exists!")
                if sequence == -1:
                    msg_data['Seq'] = (seq)%window_size
                    seq = (seq+1)%window_size
                else:
                    msg_data['Seq'] = sequence%window_size
                self.check_valid_device(sender_device,receiver_device)
                self.check_device_status(sender_device,receiver_device)
                utils.send_message(self.list_of_devices[sender_device],msg_data)
            except Exception as e:
                print(e)

    def selective_repeat(self,sender_device,receiver_device,text,window_size):
        """Sends Message Using Selective Repeat ARQ"""
        i = 0
        msg_data = text.split()
        while(i<len(msg_data)):
            if i<len(msg_data):
                self.send_msg(sender_device, receiver_device, msg_data[i],window_size,i)
                i+=1
            if i<len(msg_data):
                threading.Thread(target=self.send_msg,args=(sender_device, receiver_device, msg_data[i],window_size,i)).start()
                i+=1
            if i <len(msg_data):
                threading.Thread(target=self.send_msg,args=(sender_device, receiver_device, msg_data[i],window_size,i)).start()
                i+=1 
            if i<len(msg_data):  
                threading.Thread(target=self.send_msg,args=(sender_device, receiver_device, msg_data[i],window_size,i)).start()
                i+=1

    def make_active(self,number):
        """Make Device Active."""
        self.list_of_devices[number].active = True

    def make_inactive(self,number):
        """Make Device InActive."""
        self.list_of_devices[number].active = False

    def collision_domain_util(self,dev,visited):
        """Util Function To Calculate Collision Domain."""
        visited[dev.id]=1
        cd = 0
        if type(dev)== layer2_devices.Switch or type(dev) == layer2_devices.Bridge:
            for i in dev.connected_to:
                if not visited[i.id]:
                    visited[i.id] = 1
                    cd+=1
            for i in dev.connected_to:
                if not visited[i.id]:
                    cd += self.collision_domain_util(i, visited)
            return cd
        elif type(dev) == devices.hubs:
            to_add = True
            for i in dev.connected_to:
                if visited[i.id]==1:
                    to_add = False
                if  visited[i.id]==0:
                    visited[i.id] = 1
                    cd += self.collision_domain_util(i, visited)
            if to_add:
                cd +=1
            return cd
        else:
            return 0

    def get_collision_domain(self):
        """Function To Check Collision Domain In the Network"""
        switches = [i for i in self.list_of_devices if type(i)==layer2_devices.Switch ]
        bridges = [i for i in self.list_of_devices if type(i)==layer2_devices.Bridge]
        hubs = [i for i in self.list_of_devices if type(i)==devices.hubs ]
        visited = [0] * self.deivces_counter
        cd = 0
        for i in switches:
            if not visited[i.id]:
                cd += self.collision_domain_util(i, visited)
        for i in bridges:
            if not visited[i.id]:
                cd += self.collision_domain_util(i, visited)
        for i in hubs:
            if not visited[i.id]:
                cd += self.collision_domain_util(i, visited)
        return cd
""""Code For Token Passing. Switches Token After Every 0.5 secs"""
token = 0
def get_token(device_counter):
    global token
    while True:
        token = (token+1)%device_counter
        time.sleep(0.5)
    
#Driver Code Example

N1 = Network()
N1.add_device(devices.devices(N1.deivces_counter,devices.generate_mac_address(),IPNetwork('10.0.0.2/8'),IPNetwork('10.0.0.1/8'),process.HTTP(654),0))
N1.add_device(devices.devices(N1.deivces_counter,devices.generate_mac_address(),IPNetwork('10.0.0.3/8'),IPNetwork('10.0.0.1/8'),process.HTTP(580),0))
N1.add_device(devices.devices(N1.deivces_counter,devices.generate_mac_address(),IPNetwork('40.0.0.2/8'),IPNetwork('40.0.0.1/8'),process.HTTP(801),1))
N1.add_device(devices.devices(N1.deivces_counter,devices.generate_mac_address(),IPNetwork('40.0.0.3/8'),IPNetwork('40.0.0.1/8'),process.HTTP(504),1))
# N1.add_device(devices.devices(N1.deivces_counter,devices.generate_mac_address(),'10.0.0.3','a'))
# N1.add_device(devices.devices(N1.deivces_counter,devices.generate_mac_address(),'10.0.0.4','a'))
# N1.add_device(devices.devices(N1.deivces_counter,devices.generate_mac_address(),'10.0.0.5','a'))
# N1.add_device(devices.devices(N1.deivces_counter,devices.generate_mac_address(),'10.0.0.6','b'))
# N1.add_device(devices.devices(N1.deivces_counter,devices.generate_mac_address(),'10.0.0.7','b'))
# N1.add_device(devices.devices(N1.deivces_counter,devices.generate_mac_address(),'10.0.0.8','b'))
# N1.add_device(devices.devices(N1.deivces_counter,devices.generate_mac_address(),'10.0.0.9','b'))
# N1.add_device(devices.devices(N1.deivces_counter,devices.generate_mac_address(),'10.0.0.10','b'))
N1.add_hub(devices.hubs(N1.deivces_counter,1))
N1.add_hub(devices.hubs(N1.deivces_counter,0))
# N1.add_switch(layer2_devices.Switch(N1.deivces_counter,devices.generate_mac_address(),['a','b']))
r1 = router.Router(N1.deivces_counter,3)
r1.config_interface_ip(0,IPNetwork('10.0.0.1/8'))
r1.config_interface_ip(1,IPNetwork('20.0.0.2/8'))
r1.config_interface_ip(2,IPNetwork('50.0.0.2/8'))
r1.init_rip()
N1.add_router(r1)
r2 = router.Router(N1.deivces_counter,3)
r2.config_interface_ip(1,IPNetwork('40.0.0.1/8'))
r2.config_interface_ip(0,IPNetwork('30.0.0.2/8'))
r2.config_interface_ip(2,IPNetwork('50.0.0.1/8'))
r2.init_rip()
N1.add_router(r2)
r3 = router.Router(N1.deivces_counter,2)
r3.config_interface_ip(1,IPNetwork('20.0.0.1/8'))
r3.config_interface_ip(0,IPNetwork('30.0.0.1/8'))
r3.init_rip()
N1.add_router(r3)
token_gen = threading.Thread(target=get_token,args=(N1.device_counter,))
token_gen.start()
N1.connect_devices(0,4)
N1.connect_devices(1,4)
N1.connect_devices(2,5)
N1.connect_devices(3,5)
N1.connect_devices(4,6,0)
N1.connect_devices(5,7,1)
N1.connect_devices(7,8,0)
N1.connect_devices(6,8,1)
N1.connect_devices(6,7,2)
rs = [r1,r2,r3]
for m in range(len(rs)):
    for n in rs:
        n.make_RIP_table(rs)
for n in rs:
    print(n.router_table)
# N1.connect_devices(1,10)
# N1.connect_devices(2,10)
# N1.connect_devices(3,10)
# N1.connect_devices(4,10)
# N1.connect_devices(5,11)
# N1.connect_devices(6,11)
# N1.connect_devices(7,11)
# N1.connect_devices(8,11)
# N1.connect_devices(9,11)
# N1.connect_devices(10,12)
# N1.connect_devices(11,12)
N1.send_msg(0,2,"Device0ToDevice1",2)

# N1.send_msg(3,1,"Device3ToDevice1",2)
# N1.send_msg(6,1,"Device6ToDevice1",2)
# N1.send_msg(1,6,"Device1ToDevice6",2)
# N1.send_msg(0,1,"Device0ToDevice1",2)

# N1.add_bridge(layer2_devices.Bridge(N1.deivces_counter,devices.generate_mac_address()))
# N1.selective_repeat(1,2,"Yo! yo i dont know if it will work... ",4)  
# N1.send_msg(1,2,"HEY! This Should Work Right?",2)
