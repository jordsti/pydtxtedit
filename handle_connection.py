'''
 Cours : LOG735
 Session : Été 2014
 Groupe : 01
 Projet : Projet: editeur de texte distribue
 Étudiants :
    Jordan Guérin
    Frederic Langlois
 Code(s) perm. :
    GUEJ06118807
    LANF07078402
 Date :
    creation:
    modification:
 ==================================================================
 Description of file

 Gestion de la boucle de connection du coter serveur ce qui comprend la reception et l'envoi des messages
 ==================================================================
'''
import threading
import socket
from packet import packet, packet_exception
import random
import hashlib
import time
import workspace_diff


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
        self.queued_packets = []

    def __generate_user_id(self):
        if self.user_id is None:
            #sha2 = hashlib.sha256()

            #nb = random.randint(0, 100000)
            #stamp = time.time()

            #data = "%d|%d|%s|%d" % (stamp, nb, self.address[0], self.address[1])

            #sha2.update(data)

            #self.user_id = sha2.hexdigest()
            self.user_id = self.master.get_username()
            self.master.debug("User id : %s" % self.user_id)

    def run(self):
        self.connected = True
        print "Connection %d started" % self.connection_id

        while self.connected:
            try:
                if len(self.queued_packets) > 0:
                    queued_packet = self.queued_packets[0]
                    self.__send(queued_packet)
                    self.queued_packets.remove(queued_packet)

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
                        self.queued_packets.append(send_packet)

                        if self.master.access_write is not None:
                            c = self.master.get_thread(self.master.access_write)
                            if c is not None:
                                p = packet()
                                p.packet_type = packet.Message
                                p.put_field("message", "User [%s] is now possessing the write token !" % c.user_id)
                                self.queued_packets.append(p)
                        else:
                                p = packet()
                                p.packet_type = packet.Message
                                p.put_field("message", "Nobody is possessing the write token")
                                self.queued_packets.append(p)

                    else:
                        self.__error("User Id already assigned")
                elif recv_packet.packet_type == packet.Ping:
                    #sending a ping
                    self.master.debug("[%d] Ping from client (%d)" % (self.connection_id, recv_packet.packet_id))
                    send_packet = packet()
                    self.queued_packets.append(send_packet)

                elif recv_packet.packet_type == packet.Closing:
                    self.master.debug("[%d] Client is closing connection" % self.connection_id)
                    self.connected = False

                elif recv_packet.packet_type == packet.Right:
                    self.master.debug("[%d] a client is asking for the right to write, packet id: (%d)" % (self.connection_id, recv_packet.packet_id))
                    send_packet = packet()
                    send_packet.packet_type = packet.Right
                    is_waiting = False

                    if self.master.access_write is None:
                        self.master.access_write = self.connection_id
                        access = True
                        self.__write_right_update()
                    else:
                        self.master.debug("[%d] a client is added to the right to write waiting list, packet id: (%d)" % (self.connection_id, recv_packet.packet_id))
                        self.master.adding_access_queued(self.connection_id)
                        access = False
                        is_waiting = True

                    send_packet.put_field("can_write", str(access))
                    send_packet.put_field("is_waiting", str(is_waiting))

                    self.queued_packets.append(send_packet)

                elif recv_packet.packet_type == packet.ReleaseRight:
                    if self.master.access_write == self.connection_id:

                        diff_data = recv_packet.get_field("diff")

                        diff = workspace_diff.workspace_diff(diff_data)

                        if not diff.is_empty():
                            self.master.workspace.apply_diff(diff)
                            self.master.workspace.flush()

                            #send the diff to other client !!
                            self.__workspace_update(diff)

                        self.master.access_write = None
                        print "[%d] Releasing write access" % self.connection_id
                        send_packet = packet()
                        send_packet.packet_type = packet.Right
                        send_packet.put_field('can_write', str(False))
                        send_packet.put_field('is_waiting', str(False))
                        self.__send(send_packet)

                        if len(self.master.access_queued) > 0:
                            print "[%d] Release right someone is waiting for right" % self.connection_id
                            succeeding = self.master.access_queued[0]
                            print "[%d] next one in line is: %d" % (self.connection_id, succeeding)
                            self.master.next_in_queued()

                        else:
                            print "[%d] access_waiting is smaller <= 0" % self.connection_id
                            self.master.send_message('Write token is now free !')

                    elif self.connection_id in self.master.access_queued:
                        print "[%d] Releasing right when in waiting list: %d" % (self.connection_id, self.connection_id)
                        self.master.access_queued.remove(self.connection_id)
                        send_packet = packet()
                        send_packet.packet_type = packet.Right
                        send_packet.put_field("can_write", False)
                        send_packet.put_field("is_waiting", False)
                        self.__send(send_packet)
                    else:
                        self.__error("You don't have the write access !")

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

            #little nap for the cpu
            time.sleep(0.3)

        self.terminate()

    def __workspace_update(self, diff):
        for c in self.master.threads:
            if not c.connection_id == self.connection_id:
                p = packet()
                p.packet_type = packet.WorkspaceUpdate
                p = diff.fill_packet(p)
                c.queued_packets.append(p)


    def __write_right_update(self):
        for c in self.master.threads:
            if not c.connection_id == self.connection_id:
                p = packet()
                p.packet_type = packet.WriteUpdate
                p.put_field('id', self.user_id)
                c.queued_packets.append(p)


    def __error(self, message):
        error_packet = packet()
        error_packet.packet_type = packet.Error
        error_packet.fields['message'] = message
        print "[%d] Sending error packet..." % self.connection_id
        self.__send(error_packet)

    def __send(self, to_send):
        self.sent_packets.append(to_send)
        self.client.send(to_send.to_string())

    def next_inline(self):
        if self.master.access_write is None:
            print "next inline process"
            self.master.access_write = self.connection_id
            send_packet = packet()
            send_packet.packet_type = packet.Right
            access = True
            send_packet.put_field("can_write", str(access))
            send_packet.put_field("is_waiting", False)
            self.queued_packets.append(send_packet)
            print "Next inline packet: " + send_packet.to_string()

            self.__write_right_update()

        else:
            print "handle connection, next inline case not implemented "

    def terminate(self):
        self.connected = False
        print "Connection %d ended" % self.connection_id
        self.client.close()
        self.master.clean_connection(self)
        self.master.threads.remove(self)