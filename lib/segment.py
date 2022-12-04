import struct
from .util import *

class SegmentFlag:
    def __init__(self, flag : bytes):
        # Init flag variable from flag byte
        self.syn = flag & SYN_FLAG
        self.ack = flag & ACK_FLAG
        self.fin = flag & FIN_FLAG

    def get_flag_bytes(self) -> bytes:
        # Convert this object to flag in byte form
        return struct.pack("B", self.syn | self.ack | self.fin)

class Segment:
    # -- Internal Function --
    def __init__(self):
        # Initalize segment
        self.ack = 0
        self.seq = 0
        self.checksum = 0
        self.data = b""
        self.flag = SegmentFlag(0b00000000)

    def __str__(self):
        # Optional, override this method for easier print(segmentA)
        output = ""
        output += f"{'Sequence number':24} | {self.seq}\n"
        output += f"{'Ack number':24} | {self.ack}\n"
        output += f"{'Checksum':24} | {hex(self.checksum)}\n"
        output += f"{'Valid checksum':24} | {self.valid_checksum()}\n"
        output += f"{'Flags':24} | [SYN {self.flag.syn}] [ACK {self.flag.ack}] [FIN {self.flag.fin}]\n"
        return output

    def __calculate_checksum(self) -> int:
        # Calculate checksum here, return checksum result
        ret = 0
        # convert by mask and shift 4 bytes unsigned to 2 bytes integer
        # add upper sequence
        ret += ((0xFFFF0000 & self.seq) >> 16)
        # add lower sequence
        ret += (0x0000FFFF & self.seq)
        ret &= 0xFFFF
        # add upper ack
        ret += ((0xFFFF0000 & self.ack) >> 16)
        # add lower ack
        ret += (0x0000FFFF & self.ack)
        ret &= 0xFFFF
        # add flag in char
        ret += struct.unpack("B", self.flag.get_flag_bytes())[0]
        ret &= 0xFFFF
        # add atribut checksum
        ret += self.checksum
        ret &= 0xFFFF
        # make sum 16 bit data by 16 bit one's complement addition
        data = self.data
        for ind in range(0,len(data),2):
            buffer = data[ind:ind+2]
            if(len(buffer) == 1):
                buffer += struct.pack("x")
            ret += struct.unpack("H", buffer)[0] # add data chunk
            ret &= 0xFFFF
        # one's complement for the result
        ret =~ret
        ret &= 0xFFFF
        return ret

    # -- Setter --
    def set_header(self, header : dict):
        # Set header from dictionary
        self.ack = header["ack"]
        self.seq = header["sequence"]

    def set_payload(self, payload : bytes):
        # Set payload
        self.data = payload

    def set_flag(self, flag_list : list):
        # set flag from list
        temp_flag = 0b00000000
        for flag in flag_list:
            temp_flag |= flag
        self.flag = SegmentFlag(temp_flag)


    # -- Getter --
    def get_flag(self) -> SegmentFlag:
        # Return flag object
        return self.flag

    def get_header(self) -> dict:
        # Return header in dictionary form
        return {"sequence" : self.seq, "ack" : self.ack}

    def get_payload(self) -> bytes:
        # Return payload
        return self.data

    # -- Marshalling --
    def set_from_bytes(self, src : bytes):
        # From pure bytes, unpack() and set into python variable
        self.seq = struct.unpack("I", src[0:4])[0]
        self.ack = struct.unpack("I", src[4:8])[0]
        self.flag = SegmentFlag(struct.unpack("B", src[8:9])[0])
        self.checksum = struct.unpack("H", src[10:12])[0]
        self.data = src[12:]
        
    def get_bytes(self) -> bytes:
        # Convert this object to pure bytes
        self.checksum = self.__calculate_checksum()
        ret = b""
        ret += struct.pack("II", self.seq, self.ack)
        ret += self.flag.get_flag_bytes()
        ret += struct.pack("x")
        ret += struct.pack("H", self.checksum)
        ret += self.data
        return ret

    # -- Checksum --
    def valid_checksum(self) -> bool:
        # Use __calculate_checksum() and check integrity of this object
        return self.__calculate_checksum() == 0
