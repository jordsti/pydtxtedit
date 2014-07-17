__author__ = 'JordSti'
import threading
import socket
from packet import packet, packet_exception
import random
import hashlib
import time


#global vars
current_connection_id = 0


def get_connection_id():
    global current_connection_id
    cid = current_connection_id
    current_connection_id += 1
    return cid


class handle_connection(threading.Thread):

    (BufferSize) = 2048

    def __init__(self, client, address, master):
        threading.Thread.__init__(self)
        self.address = address
        self.connection_id = get_connection_id()
        self.client = client
        self.master = master
        self.connected = False
        self.buffer_size = self.BufferSize
        self.user_id = None

        self.sent_packets = []

    def __generate_user_id(self):
        if self.user_id is None:
            sha2 = hashlib.sha256()

            nb = random.randint(0, 100000)
            stamp = time.time()

            data = "%d|%d|%s|%d" % (stamp, nb, self.address[0], self.address[1])

            sha2.update(data)

            self.user_id = sha2.hexdigest()
            self.master.debug("User id : %s" % self.user_id)

    def run(self):
        self.connected = True
        print "Connection %d started" % self.connection_id

        while self.connected:
            try:
                recv_data = self.client.recv(self.buffer_size)
                try:
                    recv_packet = packet(recv_data)
                except packet_exception as e:
                    self.master.debug("[%d] Invalid Packet, closing connection" % self.connection_id)
                    self.connected = False

                if recv_packet.packet_type == packet.ConnectionInit:
                    if self.user_id is None:
                        self.__generate_user_id()
                        send_packet = packet()
                        send_packet.packet_type = packet.UserIdAssignation
                        send_packet.fields['user_id'] = self.user_id
                        send_packet.fields['workspace'] = self.master.workspace.get_data()
                        self.__send(send_packet)
                    else:
                        self.__error("User Id already assigned")
                elif recv_packet.packet_type == packet.Ping:
                    #sending a ping
                    self.master.debug("[%d] Ping from client (%d)" % (self.connection_id, recv_packet.packet_id))
                    send_packet = packet()
                    self.__send(send_packet)
                elif recv_packet.packet_type == packet.Closing:
                    self.master.debug("[%d] Client is closing connection" % self.connection_id)
                    self.connected = False
                elif recv_packet.packet_type == packet.Right:
                    self.master.debug("[%d] a client is asking for the right to write, packet id: (%d)" % (self.connection_id, recv_packet.packet_id))
                    send_packet = packet()
                    send_packet.packet_type = packet.Right
                    if self.master.access_write is None:
                        self.master.access_write = self.connection_id
                        access = True
                    else:
                        access = False
                    send_packet.put_field("write", str(access))
                    self.__send(send_packet)
                else:
                    # nothing to send
                    send_packet = packet()
                    self.__send(send_packet)

            except socket.timeout:
                #timeout hit
                print "[%d] Client timed out, terminating thread" % self.connection_id
                self.connected = False

            except socket.error as e:
                self.master.debug("socket.error (%d, %s)" % (e.errno, e.strerror))
                if e.errno == 10054:
                    print "Connection closed by the client..."
                    self.connected = False
                    #todo some cleanup if he gots the write right on the workspace

            #little nap for the cpu
            time.sleep(0.3)

        self.terminate()

    def __error(self, message):
        error_packet = packet()
        error_packet.packet_type = packet.Error
        error_packet.fields['message'] =  message
        print "[%d] Sending error packet..." % self.connection_id
        self.__send(error_packet)

    def __send(self, to_send):
        self.sent_packets.append(to_send)
        self.client.send(to_send.to_string())

    def terminate(self):
        self.connected = False
        print "Connection %d ended" % self.connection_id
        self.client.close()
        self.master.threads.remove(self)