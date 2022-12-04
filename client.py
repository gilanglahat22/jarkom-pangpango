from lib.segment import Segment
import socket
import lib.segment as segment
from lib.util import *
from lib.connection import *
class Client:
    def __init__(self):
        # Init client
        # initialize parser for client
        args = argParser("Client", ARGS_CLIENT)
        # initialize connection
        self.ip = DEFAULT_IP
        self.port = args.port
        self.broadcast_port = args.broadcast_port
        self.path = args.path
        self.show_info = args.f
        self.show_payload = args.d
        # initialize connection
        self.connection = Connection(self.ip, self.port, broadcast_port_send=True)
        # initialize server address
        self.broadcast_addr_server = (self.connection.get_broadcast_address(), self.broadcast_port)
        # configurate ip
        self.ip = self.connection.get_ip_address() 
        # do timeout
        self.timeout_ths = TIMEOUT_THS
        self.timeout = TIMEOUT

    def sendingAckNumber(self, ackNumber : int):
        # send ack number to server
        print(f"[!] [{self.server_addr[0]}:{self.server_addr[1]}] Sending ACK {ackNumber}...")
        # initiate segment
        ackResponse = Segment()
        ackResponse.set_flag([segment.ACK_FLAG])
        # initiate header
        ackResponse.set_header({"sequence" : 0, "ack" : ackNumber})
        self.connection.send_data(ackResponse, self.server_addr)
        
    def first_step(self):
        # print all the output
        print(f"Client started at {self.ip}:{self.port}")
        print("[!] Initiating Three Way Handshake...")
        print(f"[!] [Handshake] Sending broadcast SYN Request to Port {self.broadcast_addr_server[1]}")
        # do request from client to server
        synRequest = Segment()
        synRequest.set_flag([SYN_FLAG])
        # send request
        self.connection.send_data(synRequest, self.broadcast_addr_server)

    def second_step(self):
        print("[!] [Handshake] Waiting for Response from Server...")
        self.connection.set_timeout(self.timeout_ths)
        try:
            server_addr, response, checksum_result = self.connection.listen_single_segment()
            if not checksum_result:
                # cek checksum
                print("[!] Warning checksum result is not match")
                exit(1)
            print(f"[S] Getting response from server with {server_addr[0]}:{server_addr[1]}")
         # the last step is send ACK client to server
            responseFlag = response.get_flag()
            if responseFlag.syn and responseFlag.ack:
                ackRequest = Segment()
                ackRequest.set_flag([segment.ACK_FLAG])
                self.connection.send_data(ackRequest, server_addr)
                self.server_addr = server_addr
                print(f"\n[!] [Handshake] Three Way Handshake with {server_addr[0]}:{server_addr[1]} done")
            else:
                print("\n[!] [Invalid] Server SYN-ACK Handshake response invalid")
                print(f"[!] [Failed Handshake] Three Way Handshake with {server_addr[0]}:{server_addr[1]} failed")
                exit(1)
        except socket.timeout:
            print("\n[!] [Timeout] Terminate Program Because SYN-ACK Response Timeout")
            exit(1)

    def three_way_handshake(self):
        # First step is send SYN from client to server
        self.first_step()
        # Second step is listen SYN ACK from server to client
        # the last step is send ACK client to server
        self.second_step()

    def listen_file_transfer(self):
        # listen file transfer
        print("[!] [File Transfer] File Transfer Started...")
        self.connection.set_timeout(self.timeout)
        with open(self.path, "wb") as f:
            reqNumber = 0
            endFile    = False
            while not endFile:
                try:
                    addr, response, checksum_result = self.connection.listen_single_segment()
                    address_str = f"{addr[0]}:{addr[1]}"
                    if addr == self.server_addr and checksum_result:
                        seqNumber = response.get_header()["sequence"]
                        if seqNumber == reqNumber:
                            print(f"[!] [{address_str}] Sequence number match with Rn, sending Ack number {reqNumber}...")
                            f.write(response.get_payload())
                            self.sendingAckNumber(reqNumber)
                            reqNumber += 1

                        elif response.get_flag().fin:
                            endFile = True
                            print(f"[!] [{address_str}] FIN flag, Transfer file stopped...")
                            print(f"[!] [{address_str}] Sending ACK...")
                            ackResponse = Segment()
                            ackResponse.set_flag([segment.ACK_FLAG])
                            self.connection.send_data(ackResponse, self.server_addr)

                        else:
                            print("Ignoring...")
                            print(f"[!] [{address_str}] Sequence number not equal with Rn ({seqNumber} =/= {reqNumber}), ignoring...")

                    elif not checksum_result:
                        print("Ignoring segment...")
                        print(f"[!] [{address_str}] Checksum failed, ignoring segment")
                        
                except socket.timeout:
                    self.sendingAckNumber(reqNumber - 1)
                    print(f"[!] [{self.server_addr[0]}:{self.server_addr[1]}] Listening timeout, resending ACK {reqNumber-1}...")
                    
        self.connection.close_socket()

if __name__ == '__main__':
    main = Client()
    main.three_way_handshake()
    main.listen_file_transfer()
