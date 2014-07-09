__author__ = 'JordSti'
import random
import re


packet_seed = random.randint(0, 100000)
packet_iterator = 0


def get_packet_id():
    global packet_seed
    global packet_iterator

    pid = packet_iterator + packet_seed

    packet_iterator += 1

    return pid


class packet_exception(Exception):
    pass


class packet:
    (Error, Ping, ConnectionInit, UserIdAssignation, Closing) = (-1000, 0, 1, 2, 3)  # Other type to add

    def __init__(self, text_data=None):
        self.packet_id = -1
        self.packet_type = self.Ping
        self.fields = {}

        if text_data is not None:
            self.__from_string(text_data)
        else:
            self.packet_id = get_packet_id()
            self.packet_type = self.Ping
            self.fields = {}

    def __from_string(self, text_data):
        packet_pattern = re.compile("\\[Packet:(?P<packet_id>[0-9]+):(?P<packet_type>[0-9]+)\\]\\((?P<packet_data>.*)\\)")

        m = packet_pattern.match(text_data)

        if m:
            self.packet_id = int(m.group("packet_id"))
            self.packet_type = int(m.group("packet_type"))
            data = m.group("packet_data")

            if len(data) > 0:
                fields = data.split(',')
                for f in fields:
                    fvars = f.split(':')
                    if len(fvars) == 2:
                        key = fvars[0]
                        fdata = fvars[1]
                        self.fields[key] = fdata
        else:
            raise packet_exception(0, "Parsing error [Raw Data: %s]" % text_data)

    def to_string(self):
        data = ""

        for k in self.fields:
            fdata = "%s:%s," % (k, self.fields[k])
            data += fdata

        data = data.rstrip(',')
        #[Packet:Id:Type](Data,...)
        data = "[Packet:%d:%d](%s)" % (self.packet_id, self.packet_type, data)
        return data
