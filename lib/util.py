import argparse

def argParser(desc : str, argsdict : "dict((type, str))")-> argparse.Namespace:
    pars = argparse.ArgumentParser(description=desc)
    for args in argsdict.keys():
        inputType, helpDesc = argsdict[args]
        if inputType is None:
            pars.add_argument(args,
                    help=helpDesc,
                    action="store_const",
                    const=True,
                    default=False)
        else:
            pars.add_argument(args,
                help=helpDesc,
                type=inputType)
    return pars.parse_args()

def get_parsed_args(self) -> argparse.Namespace:
        return self.parser.parse_args()

#Constant
DEFAULT_IP = "localhost"
DEFAULT_PORT = 5000
DEFAULT_BROADCAST_PORT = 9999
PORT_CLIENT = 5001
DEFAULT_WINDOW_SIZE = 10
#args
ARGS_CLIENT = {
            "port" : (int, "Client Port"),
            "broadcast_port" : (int, "Broadcast Port"),
            "path" : (str, "Destination Path"),
            "-f"   : (None, "Show Segment Info"),
            "-d"   : (None, "Show Payload")
    }

ARGS_SERVER = {
            "port" : (int, "Server Port"),
            "path" : (str, "Source Path"),
            "-f"   : (None, "Show Segment Info"),
            "-d"   : (None, "Show Payload")
}

#Segment size in bytes maximally
SEGMENT_SIZE = 32768

#buffer size
BUFFER_SIZE  = 2**16

# Constants for flag
SYN_FLAG = 0b00000010
ACK_FLAG = 0b00010000
FIN_FLAG = 0b00000001

# Constants for timeout
TIMEOUT_THS = 15
TIMEOUT = 0.5
ACK_TIMEOUT_TRANSFER = 0.4
