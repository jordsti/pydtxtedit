__author__ = 'JordSti'
import os
from packet import packet


class workspace:
    def __init__(self, data=""):
        self.data = ""

    def get_workspace_packet(self):
        """
        Generating a packet with all the text data
        :return:
        Forged packet
        """
        p = packet()
        p.packet_type = packet.Workspace
        p.fields['length'] = len(self.data)
        p.fields['content'] = self.data
        return p

    def flush(self):
        """
        Save tue current text data, depends on the implementation
        :return:
        """
        pass



class file_workspace(workspace):

    def __init__(self, file_path):
        workspace.__init__(self)
        self.file_path = file_path
        if file_path is not None:
            if os.path.exists(file_path):
                self.__load_file()
            else:
                #create a empty file
                self.__empty_file()

    def __empty_file(self):
        fp = open(self.file_path, 'w')
        fp.close()

    def __load_file(self):
        fp = open(self.file_path, 'r')
        text = ""

        line = fp.readline()

        while len(line) > 0:
            text += line + '\n'

        if len(line) > 0:
            text += line + '\n'

        fp.close()

        self.data = text

    def flush(self):
        fp = open(self.file_path, 'w')
        fp.write(self.data)
        fp.close()


if __name__ == '__main__':
    print "Workspace Unit Test"

    fw = file_workspace('test.txt')
    fw.data = "allo"
    fw.flush()
