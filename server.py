__author__ = 'JordSti'
import socket
import sys
from handle_connection import handle_connection


class server:

    (DefaultPort, DefaultWorkspace, MaxConnections) = (5656, 'workspace.txt', 25)
    (NormalMode, DebugMode) = (0, 1)

    def __init__(self, port=DefaultPort, workspace=DefaultWorkspace, max_connections=MaxConnections, mode=NormalMode):
        self.mode = mode
        self.port = port
        self.workspace = workspace
        self.max_connections = max_connections

        self.bind_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.run = True
        self.threads = []

    def debug(self, message):
        if self.mode == self.DebugMode:
            print "[Debug] %s" % message

        #todo logfile output

    def start(self):
        print "Starting pydtxtedit server"
        print "Listening on port %d" % self.port
        try:
            self.bind_socket.bind(('127.0.0.1', self.port))
        except socket.error as e:
            print "Unable to bind on port %d" % self.port
            self.debug("socket.error (%s, %s)" % (e.errno, e.strerror))
            self.run = False

        while self.run:
            try:
                self.bind_socket.listen(10)

                (client, address) = self.bind_socket.accept()

                print "Accepting connection from %s:%d" % (address[0], address[1])

                #thread creation

                if len(self.threads) < self.max_connections:
                    thread = handle_connection(client, address, self)
                    self.threads.append(thread)
                    thread.start()
                else:
                    print "Maximum connection hitted !"

            except socket.error as e:
                self.debug("socket.error (%s, %s)" % (e.errno, e.strerror))


if __name__ == '__main__':

    _mode = server.NormalMode
    _port = server.DefaultPort
    _workspace = server.DefaultWorkspace

    nargs = len(sys.argv)
    i = 0

    while i < nargs:
        arg = sys.argv[i]

        if arg == '-d' or arg == '--debug':
            #debug mode  switch
            _mode = server.DebugMode
            print "Debug mode"
        elif arg == '-p' or arg == '--port':
            i += 1
            if i < nargs:
                _port = int(sys.argv[i])
        elif arg == '-w' or arg == '--workspace':
            i += 1
            if i < nargs:
                _workspace = sys.argv[i]
        i += 1

    #server init
    _server = server(_port, _workspace, server.MaxConnections, _mode)
    _server.start()