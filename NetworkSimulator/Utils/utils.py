from netaddr import IPNetwork

def make_packets(sender_device,receiver_device,msg_data):
    """Function To Make Packets. Input Is Sender and Receiver Device Id And Message To Be Added."""
    msg_data = {'Data':msg_data,'header_3':[sender_device.ip,receiver_device.ip],'header_2':[sender_device.address]}
    return msg_data
def make_frames(receiver_device_mac,msg_data):
    """Makes Frame From Packets."""
    msg_data['header_2'].append(receiver_device_mac.address)
    return msg_data

def arp_request(device,msg_data):
    """ARP Request Method To Get MAC Address Using IP Address Of Receiver"""
    ret = 0
    print("ARP Request Sent By Device {}".format(device.id))
    for i in device.connected_to:
        ret = i.arp_res(msg_data,device)
        if ret != 0:
            msg_data['header_2'].append(ret.address)
    return msg_data

def send_message(d1,msg_data,ack_msg=False):
    """Function TO Send Message"""
    print("Frame : {}".format(msg_data))
    for i in d1.connected_to:
        i.reply(msg_data,d1,ack_msg)

def swap_address(array):
    """Swaping Method"""
    temp = array[0]
    array[0] = array[1]
    array[1] = temp
    return array

def generate_ack(msg_data):
    """Provides Proper Number To ACK. Also Swaps Sender And Receiver Address"""
    msg_data['Data'] = 'ACK For Frame {}'.format(msg_data['Seq'])
    msg_data['header_3'] = swap_address(msg_data['header_3'])
    msg_data['header_2'] = swap_address(msg_data['header_2'])
    return msg_data

def check_subnet(ip1,ip2):
    """Checks If IP Exists In That Subnet."""
    # 225 = Broadcast Address, 0 = Network Address
    subnet = "255.255.0.0"
    if IPNetwork("{}/{}".format(ip1,subnet)) == IPNetwork("{}/{}".format(ip2,subnet)):
        return True
    return False
