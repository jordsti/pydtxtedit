'''
 Cours : LOG735
 Session : Ete 2014
 Groupe : 01
 Projet : editeur de texte distribue
 Etudiants :
    Jordan Guerin
    Frederic Langlois
 Code(s) perm. :
    GUEJ06118807

 ==================================================================
 Description of file

 Gestion de la boucle de connection du coter client ce qui comprend la reception et l'envoi des messages
 ==================================================================
'''
from PyQt4 import QtCore
import client
from packet import packet


class client_thread(QtCore.QThread):

    workspace_received = QtCore.pyqtSignal(object)
    write_status_changed = QtCore.pyqtSignal(object)
    write_status_quo = QtCore.pyqtSignal(object)
    write_update = QtCore.pyqtSignal(object)
    user_assigned = QtCore.pyqtSignal(object)
    message_received = QtCore.pyqtSignal(object)

    def __init__(self, form, hostname, port):
        QtCore.QThread.__init__(self)
        self.form = form
        self.hostname = hostname
        self.port = port
        self.client = client.client(self.hostname, self.port, self.form.mode)
        self.right_updated = None
        self.client.workspace_received = self.__workspace_received
        self.client.write_status_changed = self.__write_status_changed
        self.client.write_status_quo = self.__write_status_quo  # todo to be removed
        self.client.write_update = self.__write_update
        self.client.user_assigned = self.__user_assigned
        self.client.message_received = self.__message_received

    def __message_received(self, message):
        self.message_received.emit(message)

    def __user_assigned(self):
        self.user_assigned.emit(self.client.user_id)

    def __write_update(self, user_id):
        self.write_update.emit(user_id)

    def __write_status_quo(self, status):
        self.write_status_changed.emit(status)
        if status.is_waiting:
            self.form.append_log("You are on the waiting list for the right")
        else:
            print "client form write status quo case not expected value: " + str(status.can_write)

    def __write_status_changed(self, status):
        self.write_status_changed.emit(status)
        if status.can_write:
            print "I can write " + str(status.can_write)
            self.form.append_log("You possess the right to write.")
        elif status.is_waiting:
            print "I can't write: " + str(status.can_write)
            self.form.append_log("You are now in the waiting list...")
        else:
            self.form.append_log("You do not possess the right to write anymore.")

    def __workspace_received(self, workspace):
        self.workspace_received.emit(workspace)

    def __right_updated(self, enabled):
        if self.right_updated is not None:
            self.right_updated(enabled)

    def run(self):
        if self.client.connect():
            self.form.append_log("Connected to %s:%d" % (self.hostname, self.port))
            self.form.lbl_status_value.setText("Connected")
            self.client.disconnected = self.disconnected

            self.form.btn_write_right.setEnabled(True)

            self.client.loop()
        else:
            self.form.append_log("Unable to etablish a connection with %s:%d" % (self.hostname, self.port))

        self.form.lbl_status_value.setText("Not Connected")
        self.form.connection_thread = None

    def close(self):
        self.client.close()

    def disconnected(self):
        self.form.lbl_status_value.setText("Not Connected")
        self.form.append_log("Disconnected from the server (%s:%d)" % (self.hostname, self.port))

    def send_packet(self, packet):
        self.client.queued_packets.append(packet)

    def release_right(self, diff):
        p = packet()
        p.packet_type = packet.ReleaseRight
        p = diff.fill_packet(p)

        self.client.queued_packets.append(p)
