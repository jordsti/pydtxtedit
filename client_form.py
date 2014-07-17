__author__ = 'JordSti'
from PyQt4 import QtCore, QtGui
import sys
import client_dialog
import client
from packet import packet


class client_thread(QtCore.QThread):

    workspace_received = QtCore.pyqtSignal(object) #signal for multi-thread support !
    write_status_changed = QtCore.pyqtSignal(object)

    def __init__(self, form, hostname, port):
        QtCore.QThread.__init__(self)
        self.form = form
        self.hostname = hostname
        self.port = port
        self.client = client.client(self.hostname, self.port, self.form.mode)
        self.right_updated = None
        self.client.workspace_received = self.__workspace_received
        self.client.write_status_changed = self.__write_status_changed

    def __write_status_changed(self, can_write):
        self.write_status_changed.emit(can_write)

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

            #todo some event handling with client
            self.form.btn_write_right.setEnabled(True)

            #TODO send packet

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

    def release_right(self):
        p = packet()
        p.packet_type = packet.ReleaseRight
        #todo need to send workspace diff with this
        self.client.queued_packets.append(p)


class client_form(QtGui.QMainWindow):

    (DefaultWidth, DefaultHeight) = (500, 600)

    def __init__(self, mode):
        super(client_form, self).__init__()
        self.mode = mode
        self.w_width = self.DefaultWidth
        self.w_height = self.DefaultHeight
        self.connection_thread = None
        self.__init_menu()
        self.__init_components()

    def __init_menu(self):
        self.menu = self.menuBar()

        self.connect_server = QtGui.QAction("Connect...", self)
        self.connect_server.triggered.connect(self.connect_dialog)

        self.disconnect_server = QtGui.QAction("Disconnect", self)
        self.disconnect_server.triggered.connect(self.disconnect_action)

        self.quit_action = QtGui.QAction("Quit", self)
        self.quit_action.triggered.connect(self.quit)

        self.file_menu = self.menu.addMenu("&File")
        self.file_menu.addAction(self.connect_server)
        self.file_menu.addAction(self.disconnect_server)
        self.file_menu.addAction(self.quit_action)

    def __init_components(self):
        self.setWindowTitle("pydTxtEdit : Distributed Text Editor")
        self.setMinimumWidth(self.w_width)
        self.setMinimumHeight(self.w_height)
        self.main_widget = QtGui.QWidget()
        self.main_widget.setGeometry(0, 0, self.w_width, self.w_height)

        self.setCentralWidget(self.main_widget)
        self.grid = QtGui.QGridLayout()
        self.grid.setSpacing(10)

        self.main_widget.setLayout(self.grid)

        #buttons
        self.btn_write_right = QtGui.QPushButton("Ask Write Rights")
        self.btn_give_up_right = QtGui.QPushButton("Release right")
        self.btn_give_up_right.setEnabled(False)
        self.btn_write_right.setEnabled(False)
        self.btn_write_right.clicked.connect(self.right_write_action)
        self.btn_give_up_right.clicked.connect(self.give_up_right_action)

        #textedit
        self.te_workspace = QtGui.QTextEdit()
        self.te_workspace.setEnabled(False)

        self.te_log = QtGui.QTextEdit()
        self.te_log.setEnabled(False)

        #labels
        self.lbl_status = QtGui.QLabel("Status :")
        self.lbl_status_value = QtGui.QLabel("Not Connected")
        self.lbl_textbox = QtGui.QLabel("Workspace")
        self.lbl_log = QtGui.QLabel("Message")

        #grid assign
        self.grid.addWidget(self.lbl_status, 0, 0, 1, 2)
        self.grid.addWidget(self.lbl_status_value, 0, 2, 1, 2)
        self.grid.addWidget(self.btn_write_right, 1, 0, 1, 2)
        self.grid.addWidget(self.btn_give_up_right, 1, 2, 1, 2)
        self.grid.addWidget(self.lbl_textbox, 2, 0, 1, 4)
        self.grid.addWidget(self.te_workspace, 3, 0, 4, 4)
        self.grid.addWidget(self.lbl_log, 7, 0, 1, 4)
        self.grid.addWidget(self.te_log, 8, 0, 4, 4)

        self.show()

    def workspace_received(self, workspace):
        self.te_workspace.setText(workspace.get_data())

    def write_status_changed(self, can_write):
        #todo need to handle when the user is put into a queue!
        if can_write:
            self.btn_write_right.setEnabled(False)
            self.btn_give_up_right.setEnabled(True)
        else:
            self.btn_give_up_right.setEnabled(False)
            self.btn_write_right.setEnabled(True)

    def append_log(self, message):
        #TODO WORKSPACE-05
        self.te_log.insertPlainText(message + '\n')
        self.te_log.moveCursor(QtGui.QTextCursor.End)

    def connect_dialog(self):
        d = client_dialog.connect_dialog(self)
        d.connect_trigger = self.connect_to_server

    def connect_to_server(self, hostname, port):
        #WORKSPACE-01
        if self.connection_thread is None:
            self.connection_thread = client_thread(self, hostname, port)
            self.connection_thread.right_updated = self.ninja #todo
            self.connection_thread.workspace_received.connect(self.workspace_received)
            self.connection_thread.write_status_changed.connect(self.write_status_changed)
            self.connection_thread.start()

    def disconnect_action(self):
        if self.connection_thread is not None:
            self.connection_thread.close()

    def ninja(self):
        print "ninja test"

    def right_write_action(self):
        if self.connection_thread is not None:
            #TODO WORKSPACE-03
            #TODO send msg to server to have right to write
            self.append_log("Asking server for right to write.")
            #self.btn_write_right.setEnabled(False)
            #TODO send packet
            q_packet = packet()
            q_packet.packet_type = packet.Right
            self.connection_thread.send_packet(q_packet)
            #TODO receive packet

            #if right to write
            #    self.btn_give_up_right.setEnabled(True)

    def give_up_right_action(self):
        #TODO WORKSPACE-04
        #TODO send msg to server to release right to write
        self.append_log("Asking server to give up my right to write.")
        #self.form.btn_write_right.setEnabled(True)
        #self.form.btn_give_up_right.setEnabled(False)
        if self.connection_thread is not None:
            self.connection_thread.release_right()

    def quit(self):
        self.disconnect_action()
        self.close()

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    #args parsing
    nargs = len(sys.argv)
    i = 0
    _mode = client.client.NormalMode

    while i < nargs:
        arg = sys.argv[i]

        if arg == '-d' or arg == '--debug':
            print "Debug Mode"
            _mode = client.client.DebugMode
        i += 1

    frame = client_form(_mode)
    sys.exit(app.exec_())