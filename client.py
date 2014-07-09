__author__ = 'JordSti'
import socket
from server import server  # for default port
from packet import packet
import time
import sys


class client:
    (BufferSize) = 2048

    def __init__(self, hostname, port=server.DefaultPort):
        self.hostname = hostname
        self.port = port
        self.connected = False
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.user_id = None

        self.sent_packets = []
        self.received_packets = []

        self.buffer_size = self.BufferSize

    def connect(self):
        try:
            self.socket.connect((self.hostname, self.port))

            self.connected = True
            return True
        except socket.error as e:
            print "Unable to connect to %s:%d" % (self.hostname, self.port)

        return False

    def loop(self):
        while self.connected:
            try:
                if self.user_id is None:
                    #must do connection init
                    send_packet = packet()
                    send_packet.packet_type = packet.ConnectionInit
                    self.__send(send_packet)
                    recv_packet = self.__receive()

                    if recv_packet.packet_type == packet.UserIdAssignation:
                        self.user_id = recv_packet.fields['user_id']
                        print "User Id : %s" % self.user_id
                    elif recv_packet.packet_type == packet.Error:
                        print "Error packet : %s" % recv_packet.fields['message']
                else:

                    send_packet = packet()
                    self.__send(send_packet)

                    recv_packet = self.__receive()

                    if recv_packet.packet_type == packet.Ping:
                        print "Ping from server (%d)" % recv_packet.packet_id
            except socket.error as e:
                print "Socket error [%s, %s]" % (e.errno, e.strerror)
                self.connected = False



    def __receive(self):
        sock_data = self.socket.recv(self.buffer_size)
        recv_packet = packet(sock_data)
        self.received_packets.append(recv_packet)
        return recv_packet

    def __send(self, to_send):
        self.sent_packets.append(to_send)
        self.socket.send(to_send.to_string())

    def close(self):
        if self.connected:
            send_packet = packet()
            send_packet.packet_type = packet.Closing

            self.__send(send_packet)
            self.connected = False


if  __name__ == '__main__':
    print "pydtxtedit Console client"
    print "GUI To implement..."

    _host = '127.0.0.1'
    _port = server.DefaultPort

    nargs = len(sys.argv)
    i = 0

    while i < nargs:
        arg = sys.argv[i]

        if arg == '-h' or arg == '--hostname':
            i += 1
            if i < nargs:
                _host = sys.argv[i]
        elif arg == '-p' or arg == '--port':
            i += 1
            if i < nargs:
                _port = int(sys.argv[i])
        i += 1

    _client = client(_host, _port)
    if _client.connect():
        _client.loop()