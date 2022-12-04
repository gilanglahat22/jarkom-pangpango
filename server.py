from lib.segment import Segment
import lib.segment as segment
import math
import socket
from lib.util import *
from lib.connection import *
from typing import Tuple
class Server:
    def __init__(self):
        args = argParser("Server", ARGS_SERVER)
        self.ip       = DEFAULT_IP
        self.port     = args.port
        self.path     = args.path
        self.show_info             = args.f
        self.show_payload          = args.d
        with open(self.path, "rb") as src:
            # Read file
            src.seek(0, 2)   
            # get size of file         
            size_of_file = src.tell()  
        self.size_of_file          = size_of_file 
        self.connection            = Connection(self.ip, self.port, broadcast_port_search=True)
        self.window_size           = DEFAULT_WINDOW_SIZE
        self.segmentResult         = math.ceil(size_of_file / SEGMENT_SIZE)
        self.ip                    = self.connection.get_ip_address()
        self.ack_timeout           = ACK_TIMEOUT_TRANSFER
        self.connection.set_timeout(ACK_TIMEOUT_TRANSFER)

    def initiate_server(self):
        print(f"[!] Server started at {self.ip}:{self.port}...")
        print(f"[!] Source file | {self.path} | {self.size_of_file} bytes")
        print("[!] Listening to broadcast address for clients...")

    def listen_for_clients(self):
            self.temp_clients_connection = []
            isWaiting_Client = True
            while isWaiting_Client:
                try:
                    address, data, checksum_result = self.connection.listen_single_segment()
                    if data.get_flag().syn and address not in self.temp_clients_connection and checksum_result:
                        self.temp_clients_connection.append(address)
                        print(f"[!] Client ({address[0]}:{address[1]}) found!")
                        print(f"\nclient(s) discovered:")
                        for i, (ip, port) in enumerate(main.temp_clients_connection, start=1):
                            print(f"{i}. {ip}:{port}")
                        repeat = True
                        while(repeat):
                            ListenAgain = input("\n[?] listen again? (y/n) ")
                            if ListenAgain == "n":
                                isWaiting_Client = False
                                repeat = False
                            elif ListenAgain == "y":
                                isWaiting_Client = True
                                repeat = False
                            else:
                                print("[!] Your command is wrong, please input again!!...")
                    elif address in self.temp_clients_connection:
                        print(f"[!] Client ({address[0]}:{address[1]}) already in the list")
                except socket.timeout:
                    # nothing happen
                    pass
    
    def init_handshake(self, addressClient : Tuple[str, int]):
        # initiating step for handshake
        response_from_syn_and_ack = Segment()
        response_from_syn_and_ack.set_flag([SYN_FLAG, ACK_FLAG])
        self.connection.send_data(response_from_syn_and_ack, addressClient)

    def three_way_handshake(self, addressClient : Tuple[str, int]) -> bool:
        # Three way handshake, server-side, 1 client
        self.init_handshake(addressClient)
        address, response, checksum_result = self.connection.listen_single_segment()
        print("[!] Waiting response from client....")
        if (not response.get_flag().ack) or (not checksum_result) or (address!=addressClient):
            print("[!] Invalid response : Client ACK handshake response invalid....")
            print(f"[!] [Handshake] Handshake failed with {addressClient[0]}:{addressClient[1]}\n")
            return False
        else:
            print("[!] Valid response : Client ACK handshake response received and valid....")
            print(f"[!] [Handshake] Handshake success with {addressClient[0]}:{addressClient[1]}\n")
            return True

    def start_file_transfer(self):
        # Start file transfer
        print("\n[!] [Handshake] Initiating three way handshake with clients...\n")
        ths_address_failed = []
        # Three way handshake
        for addressClient in self.temp_clients_connection:
            print(f"[!] Sending SYN-ACK to client {addressClient[0]}:{addressClient[1]}")
            thsSuccess = self.three_way_handshake(addressClient)
            if not thsSuccess:
                # append address to failed list
                ths_address_failed.append(addressClient)
        
        print("\n[!] Cleaning address failed in client list...")
        # Remove failed address
        for i in ths_address_failed:
            for j in self.temp_clients_connection:
                if(i==j):
                    self.temp_clients_connection.remove(i)

        print("\n[!] Commencing file transfer...")
        
        # Now, file client was free for failed address client
        # Do file transfer
        for addressClient in self.temp_clients_connection:
            self.file_transfer(addressClient)

    def file_transfer(self, addressClient : tuple):
        
        with open(self.path, "rb") as f:
            # initiati file transfer with sec number 0
            seqNum            = 0
            seqNumMax         = 0
            window_size       = self.window_size
            seqWindow         = min(seqNum + window_size, self.segmentResult) - seqNum
        
            # File transfer
            while seqNum < self.segmentResult:
                # Sending segments within window
                for i in range(seqWindow):
                    segmentInfo = Segment()
                    f.seek(SEGMENT_SIZE * (seqNum + i))
                    segmentInfo.set_payload(f.read(SEGMENT_SIZE))
                    segmentInfo.set_header({"sequence" : seqNum + i, "ack" : 0})
                    self.connection.send_data(segmentInfo, addressClient)
                    print(f"[!] [{addressClient[0]}:{addressClient[1]}] Sending segment with sequence number {seqNum + i}")

                seqNumMax = seqNum + window_size
                while seqNum < seqNumMax:
                    try:
                        addr, resp, checksum_result = self.connection.listen_single_segment()
                        address_str = f"{addr[0]}:{addr[1]}"
                        if resp.get_flag().ack and checksum_result and addr == addressClient:
                            ackNumResponse = resp.get_header()["ack"]
                            if ackNumResponse > seqNum:
                                print(f"[!] [{address_str}] ACK number {ackNumResponse} > {seqNum}, shift sequence base to {ackNumResponse + 1}")
                                seqNum    = ackNumResponse + 1
                                seqWindow = min(seqNum + window_size, self.segmentResult) - seqNum
                            
                            elif ackNumResponse == seqNum:
                                seqNum    += 1
                                seqWindow = min(seqNum + window_size, self.segmentResult) - seqNum
                                print(f"[!] [{address_str}] ACK number {ackNumResponse}, new sequence base = {seqNum}")

                            else:
                                pass
                            
                        elif addr != addressClient:
                            print("ignoring...")
                            print(f"[!] [{address_str}] Source address not match, ignoring segment")
                        
                        elif not checksum_result:
                            print(f"[!] [Failed] [{address_str}] Checksum failed {addr[0]}:{addr[1]}")

                        else:
                            print(f"[!] [Error] [{address_str}] Error in checksum")
                            
                    except socket.timeout:
                        print(f"[!] [Timeout] [{addressClient[0]}:{addressClient[1]}] ACK number {seqNum} response time out")
                        break

            # Sending FIN
            print(f"\n[!] [{addressClient[0]}:{addressClient[1]}] [Completed] Transfering File completed...\n")
            segmentInfo = Segment()
            segmentInfo.set_flag([segment.FIN_FLAG])
            self.connection.send_data(segmentInfo, addressClient)
            print(f"[!] [{addressClient[0]}:{addressClient[1]}] Sending FIN to client")
            # Waiting ACK response
            try:
                addr, response, checksum_result = self.connection.listen_single_segment()
                if response.get_flag().ack:
                    print(f"\n[!] [{addressClient[0]}:{addressClient[1]}] Connection closed\n")
                else:
                    print(f"\n[!] [{addressClient[0]}:{addressClient[1]}] Invalid ACK segment\n")
            except socket.timeout:
                print(f"\n[!] [{addressClient[0]}:{addressClient[1]}] [Timeout]\n")

if __name__ == '__main__':
    main = Server()
    main.initiate_server()
    main.listen_for_clients()
    main.start_file_transfer()