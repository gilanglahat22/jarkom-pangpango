import socket
from .util import *
from .segment import Segment
from typing import Tuple
class Connection:
    def __init__(self, ip : str, port : int, broadcast_port_send : bool = False, broadcast_port_search : bool = False):
        # Init UDP socket
        self.ip = ip
        self.port = port
        self.broadcast_addr = ""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # if broadcast_port_send is True, then use broadcast port to send data
        if broadcast_port_send:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        # if broadcast_port_search is True, then use broadcast port to search data
        if broadcast_port_search:
            self.socket.bind(("", port))
        else:
            self.socket.bind((self.ip, port))

    def get_ip_address(self) -> str:
        # Get IP address of this machine
        return self.ip

    def get_broadcast_address(self) -> str:
        # Get broadcast address of this machine
        return self.broadcast_addr

    def set_timeout(self, timeout : float):
        # Set timeout for listening
        self.socket.settimeout(timeout)

    def send_data(self, msg : "Segment", dest : Tuple[str,int]):
        # Send data to destination
        self.socket.sendto(msg.get_bytes(), dest)

    def listen_single_segment(self) -> Tuple["Segment", str]:
        # Listening single segment
        recv, address      = self.socket.recvfrom(BUFFER_SIZE)
        data            = Segment()
        data.set_from_bytes(recv)
        checksum_result = data.valid_checksum()
        return address, data, checksum_result

    def close_socket(self):
        # Close socket
        self.socket.close()
        print("[!] Connection closed")
