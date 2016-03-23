__author__ = 'Mikhail Vilgelm'

import pickle
import pprint
import unittest
import numpy as np
import ast
import os
import matplotlib.pyplot as plt


class TestbedPacket:

    @classmethod
    def serialize_data(cls, data, format='SMARTGRID'):
        if format == 'SMARTGRID':
            data = ast.literal_eval(data)
            return MeasurementPacket(asn_first=data[6:11], asn_last=data[1:6],
                                     src_addr=int(data[0]), seqN=data[11:13],
                                     hop_info=data[14:])
        elif format == 'AIRCRAFT':
            return StringPacket(data)


class StringPacket(TestbedPacket):

    def __init__(self, data):
        self.data = data

    def dump_compressed(self):
        return self.data


class MeasurementPacket(TestbedPacket):
    """
    Packet sniffed from smartgrid measurements
    """

    def __init__(self, **kwargs):
        # FIXME convert the field into integers
        self.asn_first = self.list_to_int(kwargs['asn_first'])
        self.asn_last = self.list_to_int(kwargs['asn_last'])
        self.src_addr = kwargs['src_addr']
        self.seqN = self.list_to_int(kwargs['seqN'])
        num_hops = int(len(kwargs['hop_info'])/4)  # assume 4 bytes per hop entry
        self.hop_info = []
        for i in [4*x for x in range(num_hops)]:
            self.hop_info.append({'addr': int(kwargs['hop_info'][i]),
                                  'retx': int(kwargs['hop_info'][i+1]),
                                  'freq': int(kwargs['hop_info'][i+2]),
                                  'rssi': int(kwargs['hop_info'][i+3])})
            print(self.hop_info[0])


    def dump_as_ipv6(self):
        """
        Recover full ipv6 packet from a compressed entry
        :return:
        """
        # TODO
        # recover ipv6 header
        # recover udp header
        pass

    def dump_compressed(self):
        dump = pickle.dumps(self)
        return dump.replace(b'\n', b'\\n')

    def list_to_int(self, l):
        temp = [(idx*256)*int(x) for idx, x in enumerate(l)]
        temp[0] = l[0]
        return sum(temp)


class LogProcessor:

    def __init__(self, filename):
        self.filename = filename


    def calculate_mean_delay(self):
        """

        :return: average delay
        """
        delay = []
        for line in self.yield_line():

            lines = line.split('\t')
            line = lines[0]
            print(line)

            pkt = TestbedPacket.serialize_data(line)

            # print(pkt.hop_info[0])

            if pkt.src_addr != pkt.hop_info[0]['addr']:
                # not our packet -- probably RPL
                continue

            d = pkt.asn_last - pkt.asn_first
            if d < 0:
                continue
            delay.append(d*15/1000)

        plt.figure()
        plt.boxplot(delay)
        plt.show()

        return np.mean(delay)


    def yield_line(self):
        """
        Lazy file reading
        :return:
        """
        with open(self.filename, 'r') as f:
            for line in f:
                yield line


class TestTestbedPackets(unittest.TestCase):



    def test_recovering(self):
        test_pkt = '[2, 1, 65, 1, 0, 0, 239, 64, 1, 0, 0, 234, 0, 0, 2, 3, 23, 38, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]'

        pkt = TestbedPacket.serialize_data(test_pkt)

        pkt_serialized = pkt.dump_compressed()

        pkt_recovered = pickle.loads(pkt_serialized.replace(b'\\n', b'\n'))

        print(pkt_recovered.hop_info[0])

        self.assertEqual(pkt_recovered.seqN, 234)
        self.assertEqual(pkt_recovered.src_addr, 2)

    def test_reading(self):

        p = LogProcessor(os.getenv("HOME") + '/Projects/TSCH/github/dumps/tsch_dump_2016-03-23_10:29:37')

        delay = p.calculate_mean_delay()

        print(delay)



if __name__ == '__main__':
    '''
    Testing
    '''
    unittest.main()





