__author__ = 'JordSti'
import os
from packet import packet


class workspace:
    def __init__(self, data=""):
        self.__data = data

    def clone(self):
        """
        Clone the current workspace data, useful to do a diff
        :return:
        """
        w = workspace(self.__data)
        return w

    def get_workspace_packet(self):
        """
        Generating a packet with all the text data
        :return:
        Forged packet
        """
        p = packet()
        p.packet_type = packet.Workspace
        p.fields['length'] = str(len(self.__data))
        p.fields['content'] = self.__data
        return p

    def flush(self):
        """
        Save tue current text data, depends on the implementation
        :return:
        """
        pass

    def insert(self, offset, text):
        if len(self.__data) > offset:
            self.__data = self.__data[0:offset] + text + self.__data[offset+1:]
        else:
            self.__data += text

    def append(self, text):
        self.__data += text

    def get_data(self):
        return self.__data

    def set_data(self, text):
        self.__data = text


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
            text += line
            line = fp.readline()

        if len(line) > 0:
            text += line

        fp.close()

        self.set_data(text)

    def flush(self):
        fp = open(self.file_path, 'w')
        fp.write(self.get_data())
        fp.close()


if __name__ == '__main__':
    print "Workspace Unit Test"

    fw = file_workspace('test.txt')
    #fw.__data = "allo"

    pack_str = fw.get_workspace_packet().to_string()
    print "Packet test"
    p = packet(pack_str)

    print p.to_string()

    #clone

    w2 = fw.clone()

    w2.insert(3, "aloooooo clone !!")

    print fw.get_data()
    print w2.get_data()
