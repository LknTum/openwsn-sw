__author__ = 'Mikhail Vilgelm'

import pickle
import pprint
import unittest
import numpy as np


class TestbedPacket:

    @classmethod
    def serialize_data(cls, data, format='SMARTGRID'):
        if format == 'SMARTGRID':
            return MeasurementPacket(asn_first=data[1:6], asn_last=data[8:13],
                                     src_addr=int(data[0]), seqN=data[6:8],
                                     hop_info=data[13:])
        elif format == 'AIRCRAFT':
            return StringPacket(data)


class StringPacket(TestbedPacket):

    def __init__(self, data):
        self.data = data

    def dump_compressed(self):
        return self.data


class MeasurementPacket(TestbedPacket):
    """
    Packet sniffed from Smartgrid measurements
    """

    def __init__(self, **kwargs):
        # FIXME convert the field into integers
        self.asn_first = kwargs['asn_first']
        self.asn_last = kwargs['asn_last']
        self.src_addr = kwargs['src_addr']
        self.seqN = kwargs['seqN']
        num_hops = int(len(kwargs['hop_info'])/4)  # assume 4 bytes per hop entry
        self.hop_info = []
        for i in [4*x for x in range(num_hops)]:
            self.hop_info.append({'addr': kwargs['hop_info'][i],
                                  'retx': kwargs['hop_info'][i+1],
                                  'freq': kwargs['hop_info'][i+2],
                                  'rssi': kwargs['hop_info'][i+3]})

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
        return pickle.dumps(self)

    def get_asn_first(self):
        """
        :return: int representation of the asn
        """
        return sum([idx*256*int(x) for idx, x in enumerate(reversed(self.asn_first))])

    def get_asn_last(self):
        """

        :return: int representation of the asn
        """

        return sum([idx*256*int(x) for idx, x in enumerate(reversed(self.asn_last))])



class TestTestbedPackets(unittest.TestCase):

    def test_parsing(self):
        '''
        TODO
        :return:
        '''
        self.assertTrue(True)

    def test_recovering(self):
        test_pkt = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '0', '1', '2', '3', '4', '5', '6', '7', '8']
        pkt = TestbedPacket.serialize_data(test_pkt)

        pkt_serialized = pkt.dump_compressed()

        print(pkt_serialized)

        pkt_recovered = pickle.loads(pkt_serialized)

        self.assertEqual(pkt_recovered.seqN, test_pkt[6:8])
        self.assertEqual(pkt_recovered.src_addr, int(test_pkt[0]))


class LogProcessor:

    def __init__(self, filename):
        self.filename = filename


    def calculate_delay(self):
        """

        :return: average delay
        """
        delay = []
        for line in self.yield_line():
            pkt = pickle.loads(line.split(' '))
            delay.append(pkt.get_asn_last() - pkt.get_asn_first())
        return np.mean(delay)


    def yield_line(self):
        """
        Lazy file reading
        :return:
        """
        with open(self.filename) as f:
            for line in f:
                yield line

if __name__ == '__main__':
    '''
    Testing
    '''
    unittest.main()



