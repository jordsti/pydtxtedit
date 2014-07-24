__author__ = 'JordSti'
import socket
from server import server  # for default port
from packet import packet
import workspace
import time
import sys


class client_status:
    def __init__(self, can_write=False, is_waiting=False):
        self.can_write = can_write
        self.is_waiting = is_waiting


class client:
    (BufferSize) = 2048
    (NormalMode, DebugMode) = (0, 1)

    def __init__(self, hostname, port=server.DefaultPort, mode=NormalMode):
        self.mode = mode
        self.hostname = hostname
        self.port = port
        self.connected = False
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.user_id = None
        self.workspace = workspace.workspace()
        self.pending_diff = None

        self.can_write = False
        self.is_waiting = False

        self.workspace_received = None
        self.write_status_changed = None

        self.queued_packets = []
        self.sent_packets = []
        self.received_packets = []

        self.buffer_size = self.BufferSize

        #event handling
        self.disconnected = None

    def make_diff(self, new_text):
        new_workspace = workspace.workspace(new_text)
        diff = self.workspace.diff(new_workspace)
        if not diff.is_empty():
            self.pending_diff = diff
            print diff.to_string()
            #todo send diff with release right

    def get_client_status(self):
        return client_status(self.can_write, self.is_waiting)

    def __workspace_received(self):
        if self.workspace_received is not None:
            self.workspace_received(self.workspace)

    def __write_status_changed(self):
        if self.write_status_changed is not None:
            self.write_status_changed(self.get_client_status())
            #TODO write if you got the right
            #TODO if release before got right do we remove it from list in server ??

    def __write_status_quo(self):   #todo to be removed
        if self.write_status_quo is not None:
            #case possible: you don't have the right and ask for it ?
            self.write_status_quo(self.get_client_status())

    def debug(self, message):
        if self.mode == self.DebugMode:
            print "[Debug] %s" % message

        #output to log file maybe

    def __disconnected(self):
        if self.disconnected is not None:
            self.disconnected()

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
                        text_data = recv_packet.get_field("workspace")
                        self.workspace.set_data(text_data)
                        self.__workspace_received()
                        #print "User Id : %s" % self.user_id
                    elif recv_packet.packet_type == packet.Error:
                        print "Error packet : %s" % recv_packet.fields['message']
                else:
                    if len(self.queued_packets) > 0:
                        q_packet = self.queued_packets[0]
                        self.__send(q_packet)
                        self.debug("queued packet send %s" % q_packet.to_string())
                        self.queued_packets.remove(q_packet)
                    else:
                        send_packet = packet()
                        self.__send(send_packet)

                    recv_packet = self.__receive()

                    if recv_packet.packet_type == packet.Ping:
                        self.debug("Ping from server (%d)" % recv_packet.packet_id)

                    elif recv_packet.packet_type == packet.Right:
                        can_write = recv_packet.get_bool('write')
                        is_waiting = recv_packet.get_bool('is_waiting')
                        #FIXME why not just pass can_write in param to __write_status_changed???
                        self.can_write = can_write
                        self.is_waiting = is_waiting
                        self.__write_status_changed()
                        #else:
                        #FIXME maybe receive is number in line before he got the right ??
                        #    self.__write_status_quo()

            except socket.error as e:
                print "Socket error [%s, %s]" % (e.errno, e.strerror)
                self.connected = False
                self.__disconnected()

            time.sleep(0.2) # little break

    def __receive(self):
        sock_data = self.socket.recv(self.buffer_size)
        recv_packet = packet(sock_data)
        self.received_packets.append(recv_packet)
        return recv_packet

    def __send(self, to_send):
        self.sent_packets.append(to_send)
        self.socket.send(to_send.to_string())

    def __queued(self, to_add):
        self.queued_packets.append(to_add)

    def close(self):
        if self.connected:
            send_packet = packet()
            send_packet.packet_type = packet.Closing

            self.__send(send_packet)
            self.connected = False

            self.__disconnected()


if __name__ == '__main__':
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