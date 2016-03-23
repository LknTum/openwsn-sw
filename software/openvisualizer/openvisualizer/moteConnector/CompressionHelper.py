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
        """
        Factory method
        """
        if format == 'SMARTGRID':
            data = ast.literal_eval(data)
            return MeasurementPacket(asn_first=data[6:11], asn_last=data[1:6],
                                     src_addr=int(data[0]), seqN=data[11:13],
                                     hop_info=data[14:])
        elif format == 'AIRCRAFT':
            return StringPacket(data)


class StringPacket(TestbedPacket):
    """
    Packets sniffed from aircraft measurments
    """

    def __init__(self, data):
        self.data = data


    def dump_compressed(self):
        return self.data



class MeasurementPacket(TestbedPacket):
    """
    Packet sniffed for smartgrid measurements
    """

    def __init__(self, **kwargs):
        """
        Instantiate a measurements packet object
        :param kwargs:
        :return:
        """
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
        """
        Serialize object and return as bytes + escape the newline character
        :return:
        """
        dump = pickle.dumps(self)
        return dump.replace(b'\n', b'\\n')

    def list_to_int(self, l):
        """
        Convert a multibyte value to a single number
        :param l:
        :return:
        """
        temp = [(idx*256)*int(x) for idx, x in enumerate(l)]
        temp[0] = l[0]
        return sum(temp)


class TestTestbedPackets(unittest.TestCase):
    """
    Unit tests
    """

    def test_recovering(self):
        """
        Test whether serializing and recovering works
        :return:
        """
        test_pkt = '[2, 1, 65, 1, 0, 0, 239, 64, 1, 0, 0, 234, 0, 0, 2, 3, 23, 38, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]'

        pkt = TestbedPacket.serialize_data(test_pkt)

        pkt_serialized = pkt.dump_compressed()

        pkt_recovered = pickle.loads(pkt_serialized.replace(b'\\n', b'\n'))

        self.assertEqual(pkt_recovered.seqN, 234)
        self.assertEqual(pkt_recovered.src_addr, 2)



if __name__ == '__main__':
    '''
    Testing
    '''
    unittest.main()





